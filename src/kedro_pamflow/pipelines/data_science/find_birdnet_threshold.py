import argparse
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import glm
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path, focal_species):
    """Load and filter the dataset for a specific species."""
    data = pd.read_csv(file_path, sep=',')
    data['correct'] = (data['species'] == focal_species).astype(int)
    data['confidence'] = data['birdnet_conf']
    return data

def fit_models(data):
    """Fit null and confidence models, and return both models."""
    null_model = glm('correct ~ 1', data=data, family=sm.families.Binomial()).fit()
    conf_model = glm('correct ~ confidence', data=data, family=sm.families.Binomial()).fit()
    return null_model, conf_model

def create_aic_table(null_model, conf_model):
    """Create and return an AIC table comparing the null and confidence models."""
    aic_table = pd.DataFrame({
        'Model': ['null_model', 'conf_model'],
        'AIC': [null_model.aic, conf_model.aic]
    })
    return aic_table.sort_values(by='AIC', ascending=True)

def calculate_cutoff(conf_model, probability=0.95):
    """Calculate and return the cutoff confidence score for a given true positive rate."""
    logit_value = np.log(probability / (1 - probability))
    cutoff = (logit_value - conf_model.params['Intercept']) / conf_model.params['confidence']
    return cutoff

def plot_results(data, prediction_range_conf, predictions_conf, cutoff, proba):
    """Plot the scatter plot of data, model predictions, and the cutoff line."""
    plt.figure(figsize=(10, 6))
    
    # Scatter plot of the original data
    sns.scatterplot(x='confidence', y='correct', data=data, 
                    color='black', s=100, alpha=0.2)

    # Add the line for model predictions
    plt.plot(prediction_range_conf, predictions_conf, 
             linewidth=4, color=(0, 0.75, 1, 0.5))

    # Add the vertical line for the cutoff at 95% confidence
    plt.axvline(x=cutoff, color='red', linewidth=2)

    # Customize the plot
    plt.title(f'Confidence scores - pr(tpr={proba}) = {round(cutoff, 3)}')
    plt.xlabel('Confidence score')
    plt.ylabel('pr(BirdNET prediction is correct)')
    plt.xlim([min(prediction_range_conf), max(prediction_range_conf)])

    # Show the plot
    plt.show()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process file path and perform analysis.')
    parser.add_argument('-i', '--input', required=True, help='Input file path')
    parser.add_argument('-p', '--probability', type=float, default=0.95, help='Desired true positive probability')
    args = parser.parse_args()

    # Extract the species code from the file path
    file_path = args.input
    focal_species = file_path.split('_')[-1].replace('.csv', '')

    # Load and preprocess the data
    data = load_data(file_path, focal_species)

    # Fit models
    null_model, conf_model = fit_models(data)

    # Display the AIC table
    aic_table = create_aic_table(null_model, conf_model)
    print(aic_table)

    # Calculate predictions and the cutoff value
    prediction_range_conf = np.arange(0, 1.001, 0.001)
    predictions_conf = conf_model.predict(pd.DataFrame({'confidence': prediction_range_conf}))
    cutoff = calculate_cutoff(conf_model, args.probability)

    # Print the cutoff value
    print(f'{focal_species}')
    print(f'Cutoff for {args.probability*100}% confidence: {cutoff}')

    # Plot the results
    plot_results(data, prediction_range_conf, predictions_conf, cutoff, args.probability)

# Run the main function
if __name__ == "__main__":
    main()
