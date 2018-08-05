import pandas as pd
import numpy as np
import pytest

from pingouin.tests._tests_pingouin import _TestPingouin
from pingouin.pairwise import pairwise_ttests, pairwise_corr, pairwise_tukey

# Dataset for pairwise_ttests
n = 30
months = ['August', 'January', 'June']
# Generate random data
np.random.seed(1234)
control = np.random.normal(5.5, size=len(months) * n)
meditation = np.r_[np.random.normal(5.5, size=n),
                   np.random.normal(5.8, size=n),
                   np.random.normal(6.4, size=n)]

df = pd.DataFrame({'Scores': np.r_[control, meditation],
                   'Time': np.r_[np.repeat(months, n), np.repeat(months, n)],
                   'Group': np.repeat(['Control', 'Meditation'],
                                      len(months) * n)})

# dataset for pairwise_corr
data = pd.DataFrame({'X': np.random.normal(size=100),
                     'Y': np.random.normal(size=100),
                     'Z': np.random.normal(size=100)})

# "Pain thresholds" dataset (McClave and Dietrich, 1991) in JASP.
df_pain = pd.DataFrame({'Color': ['LB', 'LB', 'LB', 'LB', 'LB', 'DB', 'DB',
                                  'DB', 'DB', 'DB', 'LBr', 'LBr', 'LBr',
                                  'LBr', 'DBr', 'DBr', 'DBr', 'DBr', 'DBr'],
                        'Pain': [62, 60, 71, 55, 48, 63, 57, 52, 41, 43, 42,
                                 50, 41, 37, 32, 39, 51, 30, 35]})


class TestPairwise(_TestPingouin):
    """Test pairwise.py."""

    def test_pairwise_ttests(self):
        """Test function pairwise_ttests"""
        pairwise_ttests(dv='Scores', within='Time', between='Group',
                        effects='interaction', data=df, padjust='holm',
                        alpha=.01)
        pairwise_ttests(dv='Scores', within='Time', between='Group',
                        effects='all', data=df, padjust='fdr_bh')
        pairwise_ttests(dv='Scores', within='Time', between=None,
                        effects='within', data=df, padjust='none',
                        return_desc=False)
        pairwise_ttests(dv='Scores', within=None, between='Group',
                        effects='between', data=df, padjust='bonf',
                        tail='one-sided', effsize='cohen')
        pairwise_ttests(dv='Scores', within=None, between='Group',
                        effects='between', data=df,
                        export_filename='test_export.csv')
        # Wrong tail argument
        with pytest.raises(ValueError):
            pairwise_ttests(dv='Scores', within='Time', data=df, tail='wrong')
        # Wrong alpha argument
        with pytest.raises(ValueError):
            pairwise_ttests(dv='Scores', within='Time', data=df, alpha='.05')
        # Missing values
        df.iloc[[10, 15], 0] = np.nan
        pairwise_ttests(dv='Scores', within='Time', effects='within', data=df)
        # Wrong input argument
        df['Group'] = 'Control'
        with pytest.raises(ValueError):
            pairwise_ttests(dv='Scores', between='Group', data=df)

    def test_pairwise_tukey(self):
        """Test function pairwise_tukey"""
        stats = pairwise_tukey(dv='Pain', between='Color', data=df_pain)
        np.allclose([0.074, 0.435, 0.415, 0.004, 0.789, 0.037],
                    stats.loc[:, 'p-tukey'].values.round(3), atol=0.05)

    def test_pairwise_corr(self):
        """Test function pairwise_corr"""
        # Load JASP Big 5 DataSets
        pairwise_corr(data=data, method='spearman', tail='two-sided')
        # Correct for multiple comparisons
        pairwise_corr(data=data, method='spearman', tail='one-sided',
                      padjust='bonf')
        # Export
        pairwise_corr(data=data, method='spearman', tail='one-sided',
                      export_filename='test_export.csv')
        # Check with a subset of columns
        pairwise_corr(data=data, columns=['X', 'Y'])
        with pytest.raises(ValueError):
            pairwise_corr(data=data, tail='wrong')
