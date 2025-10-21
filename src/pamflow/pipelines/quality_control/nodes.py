#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitary functions to manage, check and preprocess large sampling data assiciated with passive acoustic monitoring

"""

import os
import matplotlib.pyplot as plt
from maad import sound, util
import pandas as pd
import numpy as np
import geopandas as gpd
import contextily as cx
import matplotlib.dates as mdates
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import Normalize
from matplotlib_scalebar.scalebar import ScaleBar
from adjustText import adjust_text
import logging
from pamflow.pipelines.quality_control.utils import concat_audio
import datetime

logger = logging.getLogger(__name__)

def format_number(n):
    """ Formats a number with thin spaces as thousand separators for improved readability."""
    return f"{n:,}".replace(",", "\u2009")

def plot_sensor_performance(media):
    """Plots sensor performance to provide an overview of the sampling effort.

    This node visualizes the number of recordings per deployment over time.
    The input corresponds to the catalog entry `media@pamDP`, and the outputs
    are stored as a matplotlib figure summarizing the deployment activity and
    a processed DataFrame summarizing the number of recordings per deployment
    and day. The outputs are stored in the catalog as `sensor_deployment_plot@matplotlib`
    and `sensor_deployment_data@pandas`.

    Parameters
    ----------
    media : pandas.DataFrame
        A DataFrame containing metadata of media files, following the pamDP.media format.
        This is loaded from the catalog entry `media@pamDP`.

    Returns
    -------
    tuple
        - matplotlib.figure: A figure showing the deployment activity over time.
          This is stored in the catalog as `sensor_deployment_plot@matplotlib`.
        - pandas.DataFrame: A processed DataFrame summarizing the number of recordings
          per deployment and day. This is stored in the catalog as `sensor_deployment_data@pandas`.
    """

    # Group recordings by day
    media["timestamp"] = pd.to_datetime(media["timestamp"]).dt.date
    media_out = (
        media.groupby(["deploymentID", "timestamp"]).size().reset_index(name="count")
    )
    media_out.sort_values(by=["deploymentID", "timestamp"], inplace=True)

    # Sort the DataFrame based on the first date
    media_out["first_date"] = media_out.groupby("deploymentID")["timestamp"].transform(
        "max"
    )
    media_out = media_out.sort_values(by="first_date")

    # Get temporal coverage
    temporal_coverage = (media.timestamp.max() - media.timestamp.min()).days

    # Plot settings
    # Dynamically adjust figure size
    unique_sensors = media_out["deploymentID"].nunique()
    unique_dates = media_out["timestamp"].nunique()
    width = min(max(6, unique_dates * 0.3), 12)
    height = min(max(4, unique_sensors * 0.3), 9)

    # Define scatter plot sizes based on 'count' (ensuring they match actual sizes)
    sizes = (media_out["count"] - media_out["count"].min() + 1) * 3  # Example scaling

    # Create a modified version of the 'Blues' colormap
    Blues_mod = mpl.colors.LinearSegmentedColormap.from_list(
        "Blues_mod", ["#b0c4de", "#08306b"]
    )
    x = "timestamp"
    y = "deploymentID"

    # Create a Normalize object for the count range
    count_min = media_out["count"].min()
    count_max = media_out["count"].max()

    # Handle the edge case where all values are equal
    if count_max == count_min:
        sizes = np.full(len(media_out), 50)
        colors = np.full(len(media_out), 1) 
        norm = None  # not needed in this case
    else:
        sizes = (media_out["count"] - count_min + 1) * 3
        norm = Normalize(vmin=count_min, vmax=count_max)
        colors = media_out["count"]
    
    # Draw scatterplot
    fig, ax = plt.subplots(figsize=[width, height])
    scatter = ax.scatter(
        media_out[x],
        media_out[y],
        s=sizes,
        c=colors,
        cmap=Blues_mod,
        norm=norm if norm else None,
        alpha=1,
    )

    # Format date
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))  # Every 7 days
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    # Add title, set axes names and set grid
    ax.grid(alpha=0.2)
    ax.set_title(
        f"Deployment timeline: {media.deploymentID.nunique()} recorders | {temporal_coverage} days",
        pad=10, fontsize=16, color="gray", weight="bold"
    )
    ax.set_xlabel("Date", fontsize=12, labelpad=8)
    ax.set_ylabel("Deployment", fontsize=12, labelpad=8)
    
    # Create legend handles
    legend_values = np.linspace(
        media_out["count"].min(), media_out["count"].max(), num=4
    ).astype(int)
    if count_max == count_min:
        # All counts are equal — one legend handle with fixed size and color
        legend_handles = [
            plt.scatter(
                [],
                [],
                s=50,  # same as scatter plot
                color=Blues_mod(1),  # same as scatter plot
                label=f"{count_min}",
                alpha=1,
            )
        ]
    else:
        # Multiple values — create gradient-based legend handles
        legend_values = np.linspace(count_min, count_max, num=4).astype(int)
        legend_handles = [
            plt.scatter(
                [],
                [],
                s=(val - count_min + 1) * 3,
                color=Blues_mod(norm(val)),
                label=f"{int(val)}",
            )
            for val in legend_values
        ]
    
    # Adjust spines
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)  # Adjust the thickness
        spine.set_color("gray")  # Change color to lighter gray

    # Add legend outside the plot
    ax.legend(
        handles=legend_handles, title="Number of\nrecordings", loc="upper left", bbox_to_anchor=(1, 1)
    )
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig, media_out


def plot_sensor_location(media_summary, deployments, plot_parameters):
    """Plots the geographic location of sensors and their recording activity.

    The inputs correspond to the catalog entries `media_summary@pandas` and
    `deployments@pamDP`. The output is stored in the catalog as
    `sensor_location_plot@matplotlib`.

    Parameters
    ----------
    media_summary : pandas.DataFrame
        A summary DataFrame for each deployment, including the start and end dates,
        number of recordings, and other statistics. Loaded from the catalog entry
        `media_summary@pandas`.

    deployments : pandas.DataFrame
        A DataFrame containing deployment metadata, including sensor locations
        (latitude and longitude). Loaded from the catalog entry `deployments@pamDP`.
        The DataFrame follows the pamDP.mdeployments format.

    plot_parameters : dict
        A dictionary containing parameters for the plot, such as colormap and figure size.

    Returns
    -------
    matplotlib.figure.Figure
        A figure showing the geographic distribution of sensors and their recording activity.
        Stored in the catalog as `sensor_location_plot@matplotlib`.
    """
    # --- Adjustable parameters from plot_parameters ---
    marker_color   = plot_parameters.get("marker_color", "#1f77b4")  # default blue
    marker_size  = plot_parameters.get("marker_size", 200)    # base size for points
    fig_height  = plot_parameters.get("fig_height", 10)        # default height 8
    fig_width   = plot_parameters.get("fig_width", 10)         # default width 8
    text_size   = plot_parameters.get("text_size", 10)        # default annotation size
    alpha   = plot_parameters.get("alpha", 0.7)        # default annotation size

    # --- Prepare data ---
    geoinfo_mics = gpd.GeoDataFrame(
        deployments[["deploymentID", "latitude", "longitude"]],
        geometry=gpd.points_from_xy(
            deployments["longitude"],
            deployments["latitude"],
        ),
        crs="EPSG:4326",
    )

    geoinfo_mics = geoinfo_mics.merge(media_summary, on="deploymentID", how="left")
    geoinfo_mics["n_recordings"] = geoinfo_mics["n_recordings"].fillna(0)
    geoinfo_mics = geoinfo_mics.astype({"n_recordings": "int"})

    # --- Figure ---
    fig, ax = plt.subplots(figsize=[fig_width, fig_height])

    # --- Scale point sizes based on number of recordings ---
    n = geoinfo_mics["n_recordings"]

    # --- Plot points ---
    scatter_plot = ax.scatter(
        geoinfo_mics.geometry.x,
        geoinfo_mics.geometry.y,
        s=marker_size,
        color=marker_color,
        alpha=alpha,
        edgecolor=marker_color,
    )

    # Add space around data (x=10%, y=10%)
    ax.margins(x=0.15, y=0.15)

    # Add basemap
    cx.add_basemap(ax, crs=geoinfo_mics.crs.to_string())

    # --- Text annotations ---
    if text_size > 0:
        texts = []
        for x, y, label in zip(
            geoinfo_mics.geometry.x,
            geoinfo_mics.geometry.y,
            geoinfo_mics.deploymentID,
        ):
            texts.append(
                ax.text(
                    x, y, label,
                    fontsize=text_size,
                    ha="center", va="center"
                )
            )
        adjust_text(
            texts,
            ax=ax,
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
            add_objects=[scatter_plot],
        )

    # Find and recolor attribution text
    for t in ax.texts:
        if "OpenStreetMap" in t.get_text():
            t.set_color("gray")      # make it gray
            t.set_alpha(0.7)         # optional transparency
    
    # Title and axis labels
    ax.set_title(f"Deployment extent: {len(geoinfo_mics)} locations", pad=10, fontsize=16, color="gray", weight="bold")
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)

    # -- Map scalebar (North arrow not necesary since lat/lon axes indicate direction) --
    # Compute meters per degree based on mean latitude
    mean_lat = geoinfo_mics.geometry.y.mean()
    meters_per_degree = 111_320 * np.cos(np.deg2rad(mean_lat))

    scalebar = ScaleBar(
        dx = meters_per_degree,
        location="upper left", 
        units="m", 
        box_alpha=0, 
        scale_loc="right", 
        height_fraction=0.005
        )  
    ax.add_artist(scalebar)

    # Equal aspect ratio
    ax.set_aspect('equal')
    plt.tight_layout()

    return fig

def plot_survey_effort(media_summary, deployments, media):
    """Plots a summary of the survey effort including number of deployments, recordings, dates, locations, and coverage.
    
    The inputs correspond to the catalog entries `media_summary@pandas`,
    `deployments@pamDP`, and `media@pamDP`. The output is stored in the catalog as
    `survey_effort@matplotlib`.

    Parameters
    ----------
    media_summary : pandas.DataFrame
        A summary DataFrame for each deployment, including the start and end dates,
        number of recordings, and other statistics. Loaded from the catalog entry
        `media_summary@pandas`.

    deployments : pandas.DataFrame
        A DataFrame containing deployment metadata, including sensor locations
        (latitude and longitude). Loaded from the catalog entry `deployments@pamDP`.
        The DataFrame follows the pamDP.mdeployments format.
    
    media : pandas.DataFrame
        A DataFrame containing metadata of media files, following the pamDP.media format.
        This is loaded from the catalog entry `media@pamDP`.

    plot_parameters : dict
        A dictionary containing parameters for the plot, such as colormap and figure size.

    Returns
    -------
    matplotlib.figure.Figure
        A grid-style infographic including number of deployments, recordings, dates, locations, and coverage. Stored in the catalog as `survey_effort@matplotlib`.
    
    """

    #%% Get data from pamDP
    n_deployments = deployments['deploymentID'].nunique()
    n_recordings = len(media)
    n_recording_time = round(media["fileLength"].sum() / 3600, 1)
    survey_dates = [pd.to_datetime(media_summary.date_ini).min().date(),
                pd.to_datetime(media_summary.date_end).max().date()]
    temporal_coverage = (survey_dates[1] - survey_dates[0]).days
    n_locations = deployments['locationID'].nunique()
    #n_locations = deployments['deploymentID'].nunique()

    # Compute spatial coverage
    if n_locations>3:
        gdf = gpd.GeoDataFrame(
            deployments, 
            geometry=gpd.points_from_xy(deployments.longitude, deployments.latitude), crs="EPSG:4326"
        )
        
        # Project to UTM (automatic choice based on centroid)
        gdf = gdf.to_crs(gdf.estimate_utm_crs())
        polygon = gdf.union_all().convex_hull  # Convex hull polygon
        area_km2 = round(polygon.area / 1_000_000)   # Area in km²
        
    else:
        area_km2 = "N/A"

    # Build table data structure
    data = [
        (n_deployments, "Deployments"),
        (f"{format_number(n_recordings)} | {n_recording_time} h", "Audio files"),
        (f"{survey_dates[0]}\n{survey_dates[1]}", "Survey dates"),
        (f"{temporal_coverage} days", "Temporal coverage"),
        (n_locations, "Locations"),
        (f"{area_km2} km$^2$", "Spatial coverage"),
    ]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")

    # Grid layout
    cols = 2
    rows = (len(data) + 1) // cols
    card_w, card_h = 0.4, 0.18
    x_margin, y_margin = 0.05, 0.05
    x_spacing, y_spacing = 0.1, 0.1

    for i, (value, label) in enumerate(data):
        row, col = divmod(i, cols)
        x = x_margin + col * (card_w + x_spacing)
        y = 1 - y_margin - (row + 1) * (card_h + y_spacing)
        
        # Draw rounded rectangle
        box = FancyBboxPatch((x, y), card_w, card_h,
                            boxstyle="round,pad=0.02,rounding_size=0.05",
                            linewidth=1, edgecolor="lightgray", facecolor="white")
        ax.add_patch(box)
        
        # Add text
        ax.text(x + card_w/2, y + card_h*0.6, value,
                ha="center", va="center", fontsize=15, weight="bold")
        ax.text(x + card_w/2, y + card_h*0.25, label,
                ha="center", va="center", fontsize=12, color="gray")

    # Add title before plt.show()
    ax.text(0.05, 0.95, "Survey Effort",
            ha="left", va="center",
            fontsize=18, color="gray", weight="bold",
            transform=ax.transAxes)
    
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 1)
    plt.tight_layout()

    return fig

def get_timelapse(
    sensor_deployment_data, media, sample_len, sample_period, sample_date, plot_params
):
    """Generates audio timelapse spectrograms for each sensor deployment.

    This node processes media files and deployment data to create spectrograms
    summarizing the acoustic activity for a selected date. The inputs correspond
    to the catalog entries `sensor_deployment_data@pandas`, `media@pamDP`,
    `sample_len@int`, `sample_period@str`, and `plot_params@dict`. The outputs
    are stored as audio files and spectrogram figures in the catalog as
    `timelapse_audio@PartitionedAudio` and `timelapse_plot@matplotlib`.

    Parameters
    ----------
    sensor_deployment_data : pandas.DataFrame
        A DataFrame summarizing the number of recordings per deployment and day.
        Loaded from the catalog entry `sensor_deployment_data@pandas`.

    media : pandas.DataFrame
        A DataFrame containing metadata of media files, following the pamDP.media format.
        Loaded from the catalog entry `media@pamDP`.

    sample_len : int
        The length of each audio sample in seconds. Loaded from the catalog entry
        `sample_len@int`.

    sample_period : str
        The resampling period for the timelapse (e.g., '1T' for 1 minute). Loaded
        from the catalog entry `sample_period@str`.

    plot_params : dict
        A dictionary containing parameters for the spectrogram plot, such as
        `nperseg`, `noverlap`, `db_range`, `fig_width`, and `fig_height`. Loaded
        from the catalog entry `plot_params@dict`.

    Yields
    ------
    tuple
        - dict: A dictionary containing audio data for each deployment, stored in the catalog
          as `timelapse_audio@PartitionedAudio`.
        - dict: A dictionary containing spectrogram figures for each deployment, stored in the
          catalog as `timelapse_plot@matplotlib`.
    """
    if sample_date is not None:
        selected_date = sample_date
    else:
        # Select the timestamp with the largest number of sensors and highest mean recordings
        # This ensures the timelapse represents the best data coverage day
        sensor_deployment_data["num_recordings_mean"] = sensor_deployment_data.groupby(
            "timestamp"
        )["count"].transform("mean")

        sensor_deployment_data["num_sensors_by_date"] = sensor_deployment_data.groupby(
            "timestamp"
        )["deploymentID"].transform("nunique")

        selected_date = sensor_deployment_data.sort_values(
            by=["num_sensors_by_date", "num_recordings_mean"], ascending=[False, False]
        )["timestamp"].unique()[0]
    
    # Timelapse data preparation
    media = media.astype({"timestamp": "datetime64[ns]"})

    df_timelapse = media[
        media["timestamp"].dt.date
        == datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
    ].copy()

    df_timelapse.loc[:, "day"] = df_timelapse["timestamp"].dt.date
    df_timelapse.set_index("timestamp", inplace=True)

    # Get parameters for plotting
    ngroups = df_timelapse.groupby(["deploymentID", "day"]).ngroups
    nperseg = plot_params["nperseg"]
    noverlap = plot_params["noverlap"]
    db_range = plot_params["db_range"]
    width = plot_params["fig_width"]
    height = plot_params["fig_height"]
    colormap = plot_params["colormap"]
    flims = plot_params["flims"]
    
    # Mix timelapse
    logger.info(f"Processing audio timelapse for {ngroups} devices:")

    for site, df_site in df_timelapse.groupby("deploymentID"):
        logger.info(f"Processing deployment: {site}...")

        # Adjust samples for timelapse
        df_site.sort_values("timestamp", inplace=True)
        df_site = df_site.resample(sample_period).first()

        # Compute timelapse
        long_wav, fs = concat_audio(
            df_site["filePath"],
            sample_len=sample_len,
        )

        # Plot spectrogram
        fig, ax = plt.subplots(figsize=(width, height))
        Sxx, tn, fn, ext = sound.spectrogram(
            long_wav,
            fs,
            nperseg=nperseg,
            noverlap=noverlap,
            flims=flims,
        )
        util.plot_spectrogram(Sxx, ext, db_range, ax=ax, colorbar=False, cmap=colormap)
        ax.text(
            0.99, 0.98,                     # move near top-right corner
            f"{site} | {selected_date}",
            color="white",
            fontsize=12,
            fontweight="bold",
            transform=ax.transAxes,
            ha="right",                     # right-align the text
            va="top",
        )
        # Define xtick positions and labels
        xtick_positions = [
            tn[0],                              # start (0h)
            tn[int(len(tn) * 0.25)],            # 1/4 of the recording (~6h)
            tn[int(len(tn) * 0.5)],             # 1/2 (~12h)
            tn[int(len(tn) * 0.75)],            # 3/4 (~18h)
            tn[-1],                             # end (~23:30h)
        ]
        xtick_labels = ["00:00", "06:00", "12:00", "18:00", "23:30"]
        ax.set_xticks(xtick_positions)
        ax.set_xticklabels(xtick_labels)
        ax.set_xlabel("Time (hh:mm)", fontsize=12)
        
        # Convert y-axis to kHz
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)  # explicitly fix tick positions
        ax.set_yticklabels([f"{y/1000:.1f}" for y in yticks])
        ax.set_ylabel("Frequency (kHz)", fontsize=12)
        plt.tight_layout()

        # Return audio and figure
        file_name = f"{site}_timelapse_{selected_date}"
        yield {file_name: (long_wav, fs)}, {file_name: fig}
        
        # Close the plot to free up memory
        plt.close(fig)



