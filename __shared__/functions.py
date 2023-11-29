import graph_tool_extras as gte
import graph_tool.draw as draw
import pandas as pd
import math
import numpy as np
import regression
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import openpyxl

def get_data_from_row(row):
    row = row.split(',')
    # devemos retornar:
        # 1. id do combo (row[6])
        # 2. nome da carta (row[0])
        # 3. ranking da carta no torneio (row[12])
        # 4. quantidade de uma mesma cópia no combo (row[2])
        # 5. categoria do torneio disputado (row[14])
        # 6. região do torneio disputado (row[16])
        # 7. rotation name (row[22])
    return row[6], row[0], row[12], row[2], row[14], row[16], row[22]

def get_or_add_vertex(g, id, bipartite):
    u = g.vertex_by_id(id)
    if u is None:
        u = g.add_vertex_by_id(id)
        # Combos are True (1) and cards are False (0)
        u['bipartite'] = bipartite
        u['color'] = 0xffffff if bipartite else 0xff0000
    return u

def get_or_add_edge(g, id1, id2):
    e = g.edge_by_ids(id1, id2)
    if e is None:
        e = g.add_edge_by_ids(id1, id2)
    return e

def main(PATH):
    FOLDER = PATH.split('.')[0]

    rotation_list = ['standard_2011','standard_2012','standard_2013','standard_2014','standard_2015','standard_2016','standard_2017','standard_2018','standard_2019','standard_2020','standard_2021','standard_2022','standard_2023']

    combo_card_list = {k: [] for k in rotation_list}
    card_ranks = {k: {} for k in rotation_list}
    card_copies = {k: {} for k in rotation_list}
    ct_cat = {k: {} for k in rotation_list} # tournament categories for each card
    ct_regions = {k: {} for k in rotation_list} # tournament regions for each card

    all_tournament_cat = []
    all_tournament_regions = []

    with open(PATH) as f:
        next(f) # skip header

        for row in f:

            # Get data from row
            combo_id, card_id, rk, cp, tcat, reg, rot = get_data_from_row(row)

            if combo_id == None and card_id == None and rk == None and cp == None and tcat == None and reg == None:
                continue

            if tcat not in all_tournament_cat:
                all_tournament_cat.append(tcat)
            if reg not in all_tournament_regions:
                all_tournament_regions.append(reg)

            if card_id in card_ranks[rot]:
                card_ranks[rot][card_id].append(int(rk))
                card_copies[rot][card_id].append(int(cp))
                ct_cat[rot][card_id].append(tcat)
                ct_regions[rot][card_id].append(reg)

            if card_id not in card_ranks[rot]:
                card_ranks[rot][card_id] = [int(rk)]
                card_copies[rot][card_id] = [int(cp)]
                ct_cat[rot][card_id] = [tcat]
                ct_regions[rot][card_id] = [reg]
                
            combo_card_list[rot].append((combo_id, card_id))

    for rot in rotation_list:
        for card in card_ranks[rot]:
            weighted_rank = 0
            for rank in card_ranks[rot][card]:
                weighted_rank += 1/math.log(rank+1)
            card_ranks[rot][card] = weighted_rank / len(card_ranks[rot][card])

        for card in card_copies[rot]:
            card_copies[rot][card] = sum(card_copies[rot][card]) / len(card_copies[rot][card])

        ct_cat_copy = ct_cat[rot].copy()
        for card_code in ct_cat_copy:
            ct_cat[rot][card_code] = []
            card = ct_cat_copy[card_code]
            # Count for each possible category and create a list of tuples (category, count)
            for category in all_tournament_cat:
                card_count = card.count(category)
                ct_cat[rot][card_code].append((category, card_count))

        ct_regions_copy = ct_regions[rot].copy()
        for card_code in ct_regions_copy:
            ct_regions[rot][card_code] = []
            card = ct_regions_copy[card_code]
            # Count for each possible region and create a list of tuples (region, count)
            for region in all_tournament_regions:
                card_count = card.count(region)
                ct_regions[rot][card_code].append((region, card_count))

    ###### Create the network ######

    centralities_betweenness = {k: {} for k in rotation_list}

    for rot in rotation_list:
        # Create undirected graph
        g = gte.Graph(directed=False)
        g.add_vp('bipartite')
        g.add_vp('color')
        unique_cards = []
        # Add vertices and edges to graph
        for combo_id, card_id in combo_card_list[rot]:
            if card_id not in unique_cards:
                unique_cards.append(card_id)
            get_or_add_vertex(g, combo_id, bipartite=1)
            get_or_add_vertex(g, card_id, bipartite=0)
            get_or_add_edge(g, combo_id, card_id)

        #layout = gte.bipartite_layout(g, 'bipartite', lambda value: bool(value))
        layout = draw.sfdp_layout(g)

        gte.move(g, layout)

        c = gte.bipartite_betweenness(g, 'bipartite', lambda value: bool(value))
        g.add_vp('betweenness', c)
        # add the betweenness centrality in centralities_betweenness[rot], which is a dict of dicts, and receives the rotation name as key
        # and the value is a dict that receives the card id as key and the betweenness value for that card as value
        for card in unique_cards:
            centralities_betweenness[rot][card] = g.vertex_by_id(card)['betweenness']

        gte.save(g, f'results/{FOLDER}/subnetworks/pokemontcg_{rot}.net.gz')

    # Regression for hipotesis 1
    dataframes = []
    for rot in rotation_list:
        data = pd.DataFrame.from_dict(card_ranks[rot], orient='index', columns=['card_ranking'])
        
        # for each card_id, which is the index of the dataframe, add the betweenness centrality value
        for card in centralities_betweenness[rot]:
            data.loc[card, 'betweenness_centrality'] = centralities_betweenness[rot][card]

        # card_copies, ct_cat, ct_regions
        for card in card_copies[rot]:
            data.loc[card, 'card_copies_avg'] = card_copies[rot][card]

        for card in ct_cat[rot]:
            for category, count in ct_cat[rot][card]:
                if category in all_tournament_cat:
                    all_tournament_cat.remove(category)
                data.loc[card, f'category_count_{category}'] = count
        if len(all_tournament_cat) > 0:
            for category in all_tournament_cat:
                data[f'category_count_{category}'] = 0
        
        for card in ct_regions[rot]:
            for region, count in ct_regions[rot][card]:
                if region in all_tournament_regions:
                    all_tournament_regions.remove(region)
                data.loc[card, f'region_count_{region}'] = count
        if len(all_tournament_regions) > 0:
            for region in all_tournament_regions:
                data[f'category_count_{region}'] = 0
            

        # normalize the columns that contain the name 'count'
        for column in data.columns:
            if 'count' in column:
                data[f'norm_{column}'] = data[column] / data[column].max()
                data.drop(column, axis=1, inplace=True)


        dataframes.append(data)

    data = pd.concat(dataframes)
    data.fillna(0, inplace=True)
    data['norm_region_count_AS_OC'] = data['norm_region_count_AS-OC']
    data.drop('norm_region_count_AS-OC', axis=1, inplace=True)

    # save data.describe().transpose() to a file
    with open(f'results/{FOLDER}/data_describe.txt', 'w') as f:
        f.write(data.describe().transpose().to_string())

    # data.corr()
    with open(f'results/{FOLDER}/data_corr.txt', 'w') as f:
        f.write(data.corr().to_string()) 


    name_var_y, name_var_x = list(data.columns)[0], list(data.columns)[1:]
    reg_result = regression.linear(data=data, formula=f'{name_var_y} ~ {" + ".join(name_var_x)}') # dependent on the left
    reg_result.micro_summary().to_excel(f'results/{FOLDER}/h1_liner_regression.xlsx')

    formula = f'{name_var_y} ~ {" + ".join([f"C({var})" for var in name_var_x])}'
    result = sm.OLS.from_formula(formula, data).fit()

    # Plot residuals for each independent variable
    for var_x in name_var_x:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(data[var_x], result.resid, alpha=0.5)
        ax.axhline(y=0, color='r', linestyle='--', linewidth=1)
        ax.set_title(f'Residuals Plot for {var_x}')
        ax.set_xlabel(var_x)
        ax.set_ylabel('Residuals')
        plt.savefig(f'results/{FOLDER}/h1_plot_residuals_{var_x}.png')
        plt.close()

    # Overall residuals plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(result.fittedvalues, result.resid, alpha=0.5)
    ax.axhline(y=0, color='r', linestyle='--', linewidth=1)
    ax.set_title('Overall Residuals Plot')
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('Residuals')
    plt.savefig(f'results/{FOLDER}/h1_plot_residuals.png')
    plt.close()


    ######## hipotesis 2 ########
    
    name_var_y, name_var_x = 'betweenness_centrality', ['card_copies_avg', 'norm_category_count_regional', 'norm_category_count_national', 'norm_category_count_international', 'norm_category_count_worlds', 'norm_category_count_others', 'norm_region_count_NA', 'norm_region_count_EU', 'norm_region_count_SA', 'norm_region_count_JP', 'norm_region_count_AS_OC']
    reg_result = regression.linear(data=data, formula=f'{name_var_y} ~ {" + ".join(name_var_x)}') # dependent on the left
    reg_result.micro_summary().to_excel(f'results/{FOLDER}/h2_liner_regression.xlsx')

    formula = f'{name_var_y} ~ {" + ".join([f"C({var})" for var in name_var_x])}'
    result = sm.OLS.from_formula(formula, data).fit()

    # Plot residuals for each independent variable
    for var_x in name_var_x:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(data[var_x], result.resid, alpha=0.5)
        ax.axhline(y=0, color='r', linestyle='--', linewidth=1)
        ax.set_title(f'Residuals Plot for {var_x}')
        ax.set_xlabel(var_x)
        ax.set_ylabel('Residuals')
        plt.savefig(f'results/{FOLDER}/h2_plot_residuals_{var_x}.png')
        plt.close()

    # Overall residuals plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(result.fittedvalues, result.resid, alpha=0.5)
    ax.axhline(y=0, color='r', linestyle='--', linewidth=1)
    ax.set_title('Overall Residuals Plot')
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('Residuals')
    plt.savefig(f'results/{FOLDER}/h2_plot_residuals.png')
    plt.close()
