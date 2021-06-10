import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import inflect
plt.style.use('ggplot')
p= inflect.engine()

df = pd.read_csv('data/pbp-2020.csv')

def is_success(row):
    '''Takes row input and returns boolean val 1 or 0 for new row "IsSuccess"'''
    if row['Down']==1 and row['Yards']/row['ToGo']>=.4:
        return 1
    elif row['Down']==2 and row['Yards']/row['ToGo']>=.60:
        return 1
    elif (row['Down']==3 or row['Down']==4) and row['Yards']>=row['ToGo']:
        return 1
    else:
        return 0
 
# Clean Data
df.drop(['Unnamed: 10', 'Unnamed: 12', 'Unnamed: 16', 'Unnamed: 17', 'Challenger', 'IsMeasurement'], axis=1, inplace=True) # Removing empty columns
df.sort_values(['GameId', 'Quarter', 'Minute', 'Second'], ascending=[True, True, False, False], inplace=True)              #Sorted by game and ordered by game time
df = df[df['PlayType'].notnull()]                                     # Removed null values associated with procedural warnings ie Two-Minute Warnings
df = df[df['PlayType']!='TIMEOUT']                                    # Removed timeouts
df = df[df['IsNoPlay']==0]                                            # Removed plays where the result of the play was called back
df['IsSuccess'] = df.apply(lambda row: is_success(row), axis=1)       # Added a column indicating whether or not the play was a success

# Useful Variables
rush_plays = df[df['IsRush']==1]                                        # Group Rush plays
pass_plays = df[df['IsPass']==1]                                        # Group Pass plays
teams = ['LV', 'MIN', 'TB', 'ARI', 'DEN', 'MIA', 'NYJ', 'CLE', 'NYG',   # List of Teams
       'BAL', 'CIN', 'HOU', 'CHI', 'IND', 'PIT', 'DAL', 'WAS', 'SEA',
       'LA', 'CAR', 'TEN', 'BUF', 'KC', 'GB', 'ATL', 'NE', 'JAX', 'SF',
       'LAC', 'PHI', 'DET', 'NO']
Is_list = ['IsRush', 'IsPass', 'IsIncomplete', 'IsTouchdown', 'IsSack', 'IsChallenge', 'IsChallengeReversed', 'IsInterception', #Stats starting with IS
    'IsFumble', 'IsPenalty', 'IsTwoPointConversion', 'IsTwoPointConversionSuccessful', 'IsPenaltyAccepted', 'IsNoPlay', 'IsSuccess']
formations = ['UNDER CENTER', 'SHOTGUN', 'NO HUDDLE SHOTGUN', 'NO HUDDLE']

# Helper Functions   

def compare_team_is_stats(stat1, stat2):
    '''Plot a comparison between two stats starting with "Is" for each team. Is stats include: ['IsRush', 'IsPass',
    'IsIncomplete', 'IsTouchdown', 'IsSack', 'IsChallenge', 'IsChallengeReversed', 'IsInterception', 'IsFumble',
    'IsPenalty', 'IsTwoPointConversion', 'IsTwoPointConversionSuccessful', 'IsPenaltyAccepted', 'IsNoPlay', 'IsSuccess]'''

    stat1_df = df.groupby('OffenseTeam').sum().sort_values(stat1, ascending=False)[stat1]
    stat2_df = df.groupby('OffenseTeam').sum().sort_values(stat2, ascending=False)[stat2]
    merged_df = stat1_df.to_frame().merge(stat2_df.to_frame(), left_index=True, right_index=True)
    x = merged_df.iloc[:,0]
    y = merged_df.iloc[:,1]
    p_stat1 = p.plural(stat1[2:])
    p_stat2 = p.plural(stat2[2:])
    fig, ax = plt.subplots()
    ax.scatter(x,y)
    ax.set_xlabel(p_stat1)
    ax.set_ylabel(p_stat2)
    ax.set_title(f'{p_stat1} VS {p_stat2}')
    for i, _x in enumerate(list(x)):
        ax.annotate(x.keys()[i], (_x,y[i]))
    fig.tight_layout()
    fig.set_size_inches(12,6)
    # fig.savefig(f'images/{p_stat1}VS{p_stat2}PerTeam')
    # return fig.show()

def avg_yards_by_down(team):
    '''This function takes a team abbreviation input and generates graphs for the average yards gained for rushing and passing plays
    for each down.'''

    team_runs = rush_plays[rush_plays['OffenseTeam']==team]
    team_passes = pass_plays[pass_plays['OffenseTeam']==team]
    rush_avgs = [team_runs[team_runs['Down']==i]['Yards'].mean() for i in range(1,5)]
    rush_counts = [team_runs[team_runs['Down']==i]['Yards'].count() for i in range(1,5)]
    pass_avgs = [team_passes[team_passes['Down']==i]['Yards'].mean() for i in range(1,5)]
    pass_counts = [team_passes[team_passes['Down']==i]['Yards'].count() for i in range(1,5)]

    fig, axs = plt.subplots(1,2)
    ax1 = axs[0]
    ax2 = axs[1]
    x = np.array([1,2,3,4])
    ax1.bar(x-.2, rush_avgs, color='red', label='Rushing Plays', width=.4, align='center')
    ax1.bar(x, pass_avgs, color='blue', label='Passing Plays',width=.4, align='edge')
    ax1.set_xlabel('Down')
    ax1.set_ylabel('Average Yards')
    ax1.set_xticks(x)
    ax1.legend()
    ax1.set_title(f'Average Yards per Down: {team}')
    ax2.bar(x-.2, rush_counts, color='red', label='Rushing Plays', width=.4, align='center')
    ax2.bar(x, pass_counts, color='blue', label='Passing Plays',width=.4, align='edge')
    ax2.set_xlabel('Down')
    ax2.set_ylabel('Total Plays')
    ax2.set_xticks(x)
    ax2.legend()
    ax2.set_title(f'Total Plays per Down: {team}')
    fig.set_size_inches(8,5)
    # return fig.show()

def stat_by_formation(stat, team):
    '''This function receives a stat and a team abbreviation and returns graphs for a given team
    comparing median yards gained for each down by type of offensive formation.'''
    if stat not in Is_list:
        temp_rush_plays = rush_plays[rush_plays['OffenseTeam']==team]
        temp_pass_plays = pass_plays[pass_plays['OffenseTeam']==team]
        fig, axs = plt.subplots(1,4)
        x= np.arange(4)
        for i, ax in enumerate(axs.flatten()):
            temp_r = temp_rush_plays[temp_rush_plays['Down'] == i+1]
            temp_p = temp_pass_plays[temp_pass_plays['Down'] == i+1]
            rush_avgs = [temp_r[temp_r['Formation']==form][stat].mean() for form in formations]
            pass_avgs =[temp_p[temp_p['Formation']==form][stat].mean() for form in formations]
            ax.bar(x-.2,rush_avgs, width=.4, color='red')
            ax.bar(x,pass_avgs, width=.4, align='edge',color='blue')
            ax.set_xticks(x)
            ax.set_xticklabels(formations, rotation=45)
            ax.set_title(f'Yards by Formation for Down {i+1}: {team}')
            ax.set_xlim(-.5,3.5)
        axs[0].set_ylabel('Average {p.plural(stat)}')
        fig.set_size_inches(18,4)
        fig.tight_layout()
        # fig.savefig(f'images/YardsbyFormationfor{team}')
        # fig.show()
    else:
        temp_rush_plays = rush_plays[rush_plays['OffenseTeam']==team]
        temp_pass_plays = pass_plays[pass_plays['OffenseTeam']==team]
        fig, axs = plt.subplots(1,4)
        x= np.arange(4)
        for i, ax in enumerate(axs.flatten()):
            temp_r = temp_rush_plays[temp_rush_plays['Down'] == i+1]
            temp_p = temp_pass_plays[temp_pass_plays['Down'] == i+1]
            rush_sums = [temp_r[temp_r['Formation']==form][stat].sum() for form in formations]
            pass_sums =[temp_p[temp_p['Formation']==form][stat].sum() for form in formations]
            ax.bar(x-.2,rush_sums, width=.4, color='red')
            ax.bar(x,pass_sums, width=.4, align='edge',color='blue')
            ax.set_xticks(x)
            ax.set_xticklabels(formations, rotation=45)
            ax.set_title(f'Yards by Formation for Down {i+1}: {team}')
            ax.set_xlim(-.5,3.5)
            ax.set_ylim(0,18)
        axs[0].set_ylabel(f'Sum of {p.plural(stat)}')
        fig.set_size_inches(18,4)
        fig.tight_layout()
        # fig.savefig(f'images/YardsbyFormationfor{team}')
        # fig.show()

def success_rate_by_down(team):
    '''This function takes a team abbreviation input and generates rate of success graphs for rushing and passing plays
    for each down.'''

    team_runs = rush_plays[rush_plays['OffenseTeam']==team]
    team_passes = pass_plays[pass_plays['OffenseTeam']==team]
    rush_rates = [team_runs[team_runs['Down']==i]['IsSuccess'].mean() for i in range(1,5)]
    pass_rates = [team_passes[team_passes['Down']==i]['IsSuccess'].mean() for i in range(1,5)]

    fig, ax = plt.subplots()
    x = np.array([1,2,3,4])
    ax.bar(x-.2, rush_rates, color='red', label='Rushing Plays', width=.4, align='center')
    ax.bar(x, pass_rates, color='blue', label='Passing Plays',width=.4, align='edge')
    ax.set_xlabel('Down')
    ax.set_ylabel('Success Rate')
    ax.set_xticks(x)
    ax.legend()
    ax.set_title(f'Success Rate of Plays per Down: {team}')
    fig.set_size_inches(8,5)
    # return fig.show()

def success_rate_by_down_and_formation(team):
    '''This function receives a team abbreviation and returns rate of success graphs for a given team for each down by type of offensive formation.'''
    temp_rush_plays = rush_plays[rush_plays['OffenseTeam']==team]
    temp_pass_plays = pass_plays[pass_plays['OffenseTeam']==team]
    fig, axs = plt.subplots(1,4)
    x= np.arange(4)
    for i, ax in enumerate(axs.flatten()):
        temp_r = temp_rush_plays[temp_rush_plays['Down'] == i+1]
        temp_p = temp_pass_plays[temp_pass_plays['Down'] == i+1]
        rush_rates = [temp_r[temp_r['Formation']==form]['IsSuccess'].mean() for form in formations]
        pass_rates =[temp_p[temp_p['Formation']==form]['IsSuccess'].mean() for form in formations]
        ax.bar(x-.2,rush_rates, width=.4, color='red')
        ax.bar(x,pass_rates, width=.4, align='edge',color='blue')
        ax.set_xticks(x)
        ax.set_xticklabels(formations, rotation=45, fontsize=10)
        ax.set_ylim(0,1)
        ax.set_title(f'Success % Down {i+1}: {team}')
    axs[0].set_ylabel('Success Rate')
    fig.set_size_inches(12,4)
    fig.tight_layout()
    # return fig.show()

def get_success_rates(team):
    '''Takes team input and returns success rate of rush/pass plays by formation for the given team. Returns a dictionary of
    dataframes with keys structured like "Down 1 Rushes" and "Down 3 Passes".'''
    rush_plays = df[df['IsRush']==1]
    pass_plays = df[df['IsPass']==1]
    success_rates = {}
    for i in range(1,5):
        temp_r = rush_plays[rush_plays['Down']==i]
        temp_p = pass_plays[pass_plays['Down']==i]
        success_rate_rush = temp_r.groupby('Formation')['IsSuccess'].mean()
        success_rate_pass = temp_p.groupby('Formation')['IsSuccess'].mean()
        success_rates[f'Down {i} Rushes'] = success_rate_rush
        success_rates[f'Down {i} Passes'] = success_rate_pass
    return success_rates

def get_beta_dist(team):
    '''This function receives a team abbreviation and returns a beta distribution for the success rate of rush and pass plays. Returns tuple like (beta_rush, 
    beta_pass, probability that passing will be more successful than rushing)'''
    temp_rush_plays = rush_plays[rush_plays['OffenseTeam']==team]
    temp_pass_plays = pass_plays[pass_plays['OffenseTeam']==team]
    rush_a = temp_rush_plays['IsSuccess'].sum()
    rush_b = temp_rush_plays['IsSuccess'].count() - rush_a
    pass_a = temp_pass_plays['IsSuccess'].sum()
    pass_b = temp_pass_plays['IsSuccess'].count() - pass_a
    rush_beta = stats.beta(rush_a+1,rush_b+1)
    pass_beta = stats.beta(pass_a+1,pass_b+1)
    return rush_beta, pass_beta, (pass_beta.rvs(size=100000) > rush_beta.rvs(size=100000)).mean()

def graph_beta_dist(team):
    posterior_r = get_beta_dist(team)[0]
    posterior_p = get_beta_dist(team)[1]
    x = np.linspace(0,1,1000)
    fig, ax = plt.subplots()
    ax.plot(x, posterior_r.pdf(x), color='red')
    ax.plot(x, posterior_p.pdf(x), color='blue')
    ax.set_xlabel('Probability')
    ax.set_ylabel('Probability Density')
    ax.set_title(f'Beta Distributions for {team}')
    ax.set_ylim(ymin=0)
    # fig.savefig(f'images/RushPassDistributions/RushPassDistribution{team}')

def get_beta_dist_league():
    '''This function receives a team abbreviation and returns a binomial distribution for the success rate of rush and pass plays. Returns tuple like (beta_rush,         beta_pass)'''
    rush_a = rush_plays['IsSuccess'].sum()
    rush_b = rush_plays['IsSuccess'].count() - rush_a
    pass_a = pass_plays['IsSuccess'].sum()
    pass_b = pass_plays['IsSuccess'].count() - pass_a
    rush_beta = stats.beta(rush_a+1,rush_b+1)
    pass_beta =stats.beta(pass_a+1,pass_b+1)
    return stats.beta(rush_a+1,rush_b+1), stats.beta(pass_a+1,pass_b+1), (pass_beta.rvs(size=100000) > rush_beta.rvs(size=100000)).mean()

def get_pval(team):
    '''This function reveives a team abbreviation and returns the pvalue for the null hypothesis that run and pass plays are equally successful.'''
    temp_rush_plays = rush_plays[rush_plays['OffenseTeam']==team]
    temp_pass_plays = pass_plays[pass_plays['OffenseTeam']==team]
    r = temp_rush_plays['IsSuccess']
    p = temp_pass_plays['IsSuccess']
    return stats.ttest_ind(r,p)[1]

def graph_confidence_interval():
    r_successes = rush_plays['IsSuccess'].sum()
    r_attempts = rush_plays['IsSuccess'].count()
    p_successes = pass_plays['IsSuccess'].sum()
    p_attempts = pass_plays['IsSuccess'].count()
    difference = (p_successes/p_attempts) - (r_successes/r_attempts)
    total_plays = r_attempts + p_attempts
    shared_sample_freq = (r_successes + p_successes) / total_plays
    shared_sample_var = total_plays * (shared_sample_freq * (1-shared_sample_freq)) / (r_attempts * p_attempts)
    difference_in_proportions = stats.norm(0, np.sqrt(shared_sample_var))
    fig, ax = plt.subplots()
    x = np.linspace(-1, 1, 10000)
    ax.plot(x, difference_in_proportions.pdf(x), linewidth=2)
    ax.set_xlim(-.05,.05)
    ax.set_xlabel('Difference in Proportions')
    ax.set_ylabel('Probability Density')
    ax.set_title('Probability Density Under $H_0$ for NFL')
    ax.fill_between(x, difference_in_proportions.pdf(x), where=(x>=difference))
    fig.set_size_inches(6,3)
    fig.tight_layout()
    fig.savefig('images/Probability Density Under H_0')
    # return fig.show()

def graph_confidence_interval_team(team):
    temp_rush_plays = rush_plays[rush_plays['OffenseTeam']==team]
    temp_pass_plays = pass_plays[pass_plays['OffenseTeam']==team]
    r_successes = temp_rush_plays['IsSuccess'].sum()
    r_attempts = temp_rush_plays['IsSuccess'].count()
    p_successes = temp_pass_plays['IsSuccess'].sum()
    p_attempts = temp_pass_plays['IsSuccess'].count()
    difference = (p_successes/p_attempts)-(r_successes/r_attempts)
    total_plays = r_attempts + p_attempts
    shared_sample_freq = (r_successes + p_successes) / total_plays
    shared_sample_var = total_plays * (shared_sample_freq * (1-shared_sample_freq)) / (r_attempts * p_attempts)
    difference_in_proportions = stats.norm(0, np.sqrt(shared_sample_var))
    fig, ax = plt.subplots()
    x = np.linspace(-1, 1, 10000)
    ax.plot(x, difference_in_proportions.pdf(x), linewidth=2)
    ax.set_xlim(-.15,.15)
    ax.set_xlabel('Difference in Proportions')
    ax.set_ylabel('Probability Density')
    ax.set_title(f'Probability Density Under $H_0$ for {team}')
    ax.fill_between(x, difference_in_proportions.pdf(x), where=(x>=difference))
    fig.set_size_inches(6,3)
    fig.tight_layout()
    # fig.savefig(f'images/Probability Density Under H_0 for {team}')
    # return fig.show()

def league_box():
    '''This function generates graphs for the average yards gained for run and pass plays for each down,
    the total amount of run and pass plays per down, and the success rate of run and pass plays per down.'''
    all_rushes = [rush_plays[rush_plays['Down']==i]['Yards'] for i in range(1,5)]
    all_passes = [pass_plays[pass_plays['Down']==i]['Yards'] for i in range(1,5)]

    fig, ax = plt.subplots()
 
    x = np.array([1,2,3,4])
    y = np.linspace(-20,100,13)
    ax.boxplot(all_rushes, positions = x-.2, widths=.25)

    ax.boxplot(all_passes, positions = x+.2, widths=.25)
    ax.set_xlabel('Down')
    ax.set_ylabel('Yards')
    ax.set_xticks(x)
    ax.set_yticks(y)
    ax.set_xticklabels([1,2,3,4])
    ax.set_title(f'Average Yards per Down')

    fig.set_size_inches(12,6)
    fig.tight_layout()
    fig.savefig('images/BoxPlot')
    # return fig.show()
