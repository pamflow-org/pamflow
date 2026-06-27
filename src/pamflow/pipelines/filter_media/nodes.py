"""
Pipeline to filter media.csv and facilitate runing the workflow in a subset of audio files
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

def filter_media(media: pd.DataFrame, deployments_filter: list) -> pd.DataFrame:
    if not deployments_filter:
        logger.info("No filter applied, using all deployments")
        return media

    available = set(media["deploymentID"].unique())
    requested = set(deployments_filter)

    # Raise error for deployments that do not exist
    missing = requested - available
    if missing:
        raise ValueError(
            f"The following deployments do not exist in media: {sorted(missing)}. "
            f"Available deployments: {sorted(available)}"
        )

    # Deployments that exist but that do not have any audio file associated
    empty = {d for d in requested if media[media["deploymentID"] == d].empty}
    if empty:
        logger.warning(f"The following deployments have no files in media: {sorted(empty)}")

    result = media[media["deploymentID"].isin(deployments_filter)]
    logger.info(f"Filtering to {len(requested)} deployments: {sorted(requested)} — {len(result)} files selected")
    return result