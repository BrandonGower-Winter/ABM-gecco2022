import argparse
import json
import matplotlib
import matplotlib.pyplot as pyplot

from matplotlib.ticker import FormatStrFormatter
import numpy as np
import scikit_posthocs as sp

from scipy import stats

import math
import os

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

array_size = 2000
iteration_multiplier = 5
runs_count = 50

#plots_ids = ['PF', '1F', '2F', '4F', '8F', '16F', '32F', '64F', '128F', 'NF']
#plots_ids = ['P', '1', '2', '4', '8', '16', '32', 'N']
#plots_ids = ['8F', '16F', '24F', '32F', '40F', '48F', '56F', '64F']
#plots_ids = ['PS', '1S', '2S', '4S', '8S', '16S', '32S', '64S', '128S', 'NS']
#plots_ids = ['PA', '1A', '2A', '4A', '8A', '16A', '32A', '64A', '128A', 'NA']
plots_ids = ['P', '1', '2', '4','8', '16', '32', '64', '128', 'N']

#plots_ids = []
levels = [50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0,95.0,100.0]

def get_scenario_data(runs: {}):

    placeholder = np.zeros((array_size, runs_count), dtype=float)
    placeholder_pop = np.zeros((array_size, runs_count), dtype=float)
    peer_placeholder = np.zeros((array_size, runs_count), dtype=float)
    sub_placeholder = np.zeros((array_size, runs_count), dtype=float)
    gini_pop = np.zeros((array_size, runs_count), dtype=float)
    settlements_pop = np.zeros((array_size, runs_count), dtype=float)
    attachments = np.zeros((array_size, runs_count), dtype=float)

    sub_requests = np.zeros((array_size * iteration_multiplier, runs_count), dtype=float)
    auth_requests = np.zeros((array_size * iteration_multiplier, runs_count), dtype=float)
    peer_requests = np.zeros((array_size * iteration_multiplier, runs_count), dtype=float)

    peer_dst_placeholder = np.zeros((array_size, runs_count, 10), dtype=float)
    sub_dst_placeholder = np.zeros((array_size, runs_count, 10), dtype=float)

    index = 0
    runs_processed = 1
    for seed in runs:
        for i in range(array_size):

            if i < len(runs[seed]['population']['number']):
                placeholder[i][index] = runs[seed]['population']['number'][i] if 'population' in runs[seed] else 0.0
                placeholder_pop[i][index] = runs[seed]['population']['total'][i] if 'population' in runs[seed] else 0.0
                peer_placeholder[i][index] = runs[seed]['peer_transfer']['mean'][i] if 'peer_transfer' in runs[seed] else 0.0
                sub_placeholder[i][index] = runs[seed]['sub_transfer']['mean'][i] if 'sub_transfer' in runs[seed] else 0.0
                gini_pop[i][index] = np.nan_to_num(runs[seed]['inequality']['gini'][i]) if 'inequality' in runs[seed] else 0.0
                settlements_pop[i][index] = runs[seed]['settlements']['count'][i] if 'settlements' in runs[seed] else 0.0
                attachments[i][index] = runs[seed]['attachment']['mean'][i] if 'attachment' in runs[seed] else 0.0

                peer_dst_placeholder[i][index] = np.nan_to_num(np.array(runs[seed]['peer_transfer']['dist'][i]))
                sub_dst_placeholder[i][index] = np.nan_to_num(np.array(runs[seed]['sub_transfer']['dist'][i]))
            else:
                placeholder[i][index] = 0
                placeholder_pop[i][index] = 0
                peer_placeholder[i][index] = 0
                sub_placeholder[i][index] = 0
                gini_pop[i][index] = 0
                settlements_pop[i][index] = 0
                attachments[i][index] = 0

                peer_dst_placeholder[i][index] = np.zeros(10)
                sub_dst_placeholder[i][index] = np.zeros(10)


        index += 1
        runs_processed += 1
        if runs_processed > runs_count:
            break

    line_data = np.zeros((28, array_size), dtype=float)
    bar_data = np.zeros((2, 3, 10), dtype=float)
    stats_data = np.zeros((3,runs_count), dtype=float)
    population_data = placeholder
    log_data = np.zeros((6, array_size * iteration_multiplier), dtype=float)

    mask = peer_placeholder[0] < sub_placeholder[0]

    for i in range(array_size):
        line_data[0][i] = np.mean(placeholder[i])
        line_data[1][i] = np.std(placeholder[i])

        line_data[2][i] = np.mean(peer_placeholder[i]) * 100.0
        line_data[3][i] = np.std(peer_placeholder[i]) * 100.0

        line_data[4][i] = np.mean(sub_placeholder[i]) * 100.0
        line_data[5][i] = np.std(sub_placeholder[i]) * 100.0

        temp = np.abs(peer_placeholder[i] - peer_placeholder[0])/(peer_placeholder[0]) * 100.0
        line_data[6][i] = np.mean(temp)
        line_data[7][i] = np.std(temp)

        temp = np.abs(sub_placeholder[i] - sub_placeholder[0])/(sub_placeholder[0]) * 100.0
        line_data[8][i] = np.mean(temp)
        line_data[9][i] = np.std(temp)

        temp = placeholder_pop[i]
        line_data[10][i] = np.mean(temp)
        line_data[11][i] = np.std(temp)

        temp = peer_placeholder[i][mask]
        line_data[12][i] = np.mean(temp)
        line_data[13][i] = np.std(temp)

        temp = sub_placeholder[i][mask]
        line_data[14][i] = np.mean(temp)
        line_data[15][i] = np.std(temp)

        temp = peer_placeholder[i][~mask]
        line_data[16][i] = np.mean(temp)
        line_data[17][i] = np.std(temp)

        temp = sub_placeholder[i][~mask]
        line_data[18][i] = np.mean(temp)
        line_data[19][i] = np.std(temp)

        line_data[20][i] = stats.shapiro(placeholder[i]).pvalue

        line_data[21][i] = line_data[0][i] / np.mean(temp)
        line_data[22][i] = line_data[1][i] / np.std(temp)

        temp =  line_data[0][i] / np.mean(settlements_pop[i])
        line_data[23][i] = np.mean(temp)

        line_data[24][i] = np.mean(gini_pop[i])

        line_data[25][i] = np.mean(attachments[i])
        line_data[26][i] = np.std(attachments[i])

        line_data[27][i] = line_data[2][i] - line_data[4][i]

        if i == 0:
            bar_data[0][0] = np.mean(peer_dst_placeholder[i], axis=0)
            bar_data[1][0] = np.mean(sub_dst_placeholder[i], axis=0)
        elif i == 999:
            bar_data[0][1] = np.mean(peer_dst_placeholder[i], axis=0)
            bar_data[1][1] = np.mean(sub_dst_placeholder[i], axis=0)
        elif i == 1999:
            bar_data[0][2] = np.mean(peer_dst_placeholder[i], axis=0)
            bar_data[1][2] = np.mean(sub_dst_placeholder[i], axis=0)

        if i > 1198:
            stats_data[0] += placeholder[i]
            stats_data[1] = peer_placeholder[i]
            stats_data[2] = sub_placeholder[i]

    for i in range(array_size * iteration_multiplier):
        log_data[0][i] = np.mean(auth_requests[i])
        log_data[1][i] = np.std(auth_requests[i])

        log_data[2][i] = np.mean(sub_requests[i])
        log_data[3][i] = np.std(sub_requests[i])

        log_data[4][i] = np.mean(peer_requests[i])
        log_data[5][i] = np.std(peer_requests[i])

    return line_data, bar_data, stats_data, log_data, population_data


def write_plot(agent_types: [], filename, data, title: str, index: [int], x_axis: str, y_axis: str,
               legend: str = 'lower right', show_std: int = -1, data_types={}, iterations = None):

    fig, ax = pyplot.subplots(dpi=200)
    ax.set_title(title)
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)

    #ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    if iterations is None:
        iterations = np.arange(array_size) * iteration_multiplier

    for agent_type in agent_types:
        if len(index) > 1:
            for i in range(len(index)):
                p = ax.plot(iterations, data[agent_type][index[i]], label=data_types[agent_type][i])
                if show_std > -1:
                    ax.fill_between(iterations, data[agent_type][index[i]] - data[agent_type][index[i] + show_std],
                                    data[agent_type][index[i]] + data[agent_type][index[i] + show_std],
                                    color=p[0].get_color(), alpha=.1)
        else:
            p = ax.plot(iterations, data[agent_type][index[0]], label=agent_type)
            if show_std > -1:
                ax.fill_between(iterations, data[agent_type][index[0]] - data[agent_type][index[0] + show_std],
                                data[agent_type][index[0]] + data[agent_type][index[0] + show_std],
                                color=p[0].get_color(), alpha=.1)

    ax.legend(loc=legend)
    ax.set_aspect('auto')

    fig.savefig(filename)
    pyplot.close(fig)


def write_bar_plot(key, filename, data, title: str, x_axis: str, y_axis: str,
               legend: str = 'upper right'):

    divide_arr = ['beginning', 'middle', 'end']

    fig, ax = pyplot.subplots(dpi=200)
    bins = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']
    x_bins = np.arange(len(bins))
    ax.set_title(title)
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)

    ax.bar(x_bins - 0.2, data[0][2], 0.4, label='Peer')
    ax.bar(x_bins + 0.2, data[1][2], 0.4, label="Sub")

    ax.set_xticks(x_bins, bins)
    ax.set_yticks(np.arange(0.0, 0.6, 0.1)) # setting the ticks

    ax.legend(loc=legend)
    ax.set_aspect('auto')

    fig.savefig(filename)
    pyplot.close(fig)


def main():
    # Process the params
    print("Parsing arguments...")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='The path to the folder containing all of the processed data',
                        required=True)
    parser.add_argument('-o', '--output', help='The path to write all of the processed data to.',
                        required=True)
    parser.add_argument('-s', '--scenario', help='The scenario name',
                        required=True)
    parser.add_argument('-v', '--verbose', help='Will print out informative information to the terminal.',
                        action='store_true')

    parser = parser.parse_args()

    data = {}
    bar_data = {}
    stats_data = {}
    log_data = {}
    pop_data = {}
    for root, _, files in os.walk(parser.path):
        for agent_type in files:
            with open(os.path.join(root, agent_type)) as json_file:
                key = agent_type[0:-5]
                data[key], bar_data[key], stats_data[key], log_data[key], pop_data[key] = get_scenario_data(json.load(json_file))

    data_types = {}

    for a in data:
        data_types[a] = ['Peer', 'Sub']

    if len(plots_ids) != 0:
        write_plot(plots_ids, '%s/population/households' % parser.output, data,
                   'Household Population for all Stress Scenarios Investigated', [0], 'Iteration (Year)', 'Population (Households)', legend='upper left')

        write_plot(plots_ids, '%s/difference.pdf' % parser.output, data,
                   '', [27], 'Iteration', 'Peer - Subordinate Transfer (%)', legend='upper left')

        write_plot(plots_ids, '%s/settlements/settlement_density' % parser.output, data,
                   '', [23], 'Iteration', 'Households per Settlement', legend='upper right')

        write_plot(plots_ids, '%s/gini/inequality' % parser.output, data,
                   '', [24], 'Iteration', 'Gini Index', legend='upper left')

        peer_heatmaps = np.zeros((len(plots_ids), 6))
        sub_heatmaps = np.zeros((len(plots_ids), 6))

        for i, id in enumerate(plots_ids):
            peer_heatmaps[i] = bar_data[id][0][2][2:8]
            sub_heatmaps[i] = bar_data[id][1][2][2:8]

        from scipy.ndimage.filters import gaussian_filter

        x_labels = plots_ids
        y_labels = ['21-30', '31-40', '41-50', '51-60', '61-70', '71-80']

        max_labels = np.round(np.linspace(0.0, 0.75, 16), 2)

        fig, ax = pyplot.subplots(dpi=200)
        ax.set_title('')
        ax.set_xlabel('Stress Scenario')
        ax.set_ylabel('Peer Transfer Property (%)')

        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)

        # Generate the pix map
        plot = ax.contourf(np.transpose(peer_heatmaps), max_labels, cmap='hot')
        fig.colorbar(plot)
        ax.set_aspect('auto')

        fig.savefig('%s/peer_heatmap' % parser.output)
        pyplot.close(fig)

        fig, ax = pyplot.subplots(dpi=200)
        ax.set_title('')
        ax.set_xlabel('Stress Scenario')
        ax.set_ylabel('Subordinate Transfer Property (%)')

        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)

        # Generate the pix map
        plot = ax.contourf(np.transpose(sub_heatmaps), max_labels, cmap='bone')
        fig.colorbar(plot)
        ax.set_aspect('auto')

        fig.savefig('%s/sub_heatmap' % parser.output)
        pyplot.close(fig)


        gini_heatmaps = np.zeros((len(plots_ids), 2000))
        y_labels = ['0', '', '2000', '', '4000', '', '6000', '', '8000', '', '10000']

        for i, id in enumerate(plots_ids):
            gini_heatmaps[i] = data[id][24]


        fig, ax = pyplot.subplots(dpi=200)
        ax.set_title('')
        ax.set_xlabel('Iterations (Year)')
        ax.set_ylabel('Gini Index')

        ax.set_xticklabels(y_labels)
        ax.set_yticklabels([''] + x_labels)

        plot = ax.imshow(gini_heatmaps, cmap='gray', interpolation='none')
        fig.colorbar(plot)
        ax.set_aspect('auto')

        fig.savefig('%s/gini_heatmap' % parser.output)
        pyplot.close(fig)

        y_labels = plots_ids
        if 'PF' in y_labels:
            y_labels.remove('PF')
        if 'PS' in y_labels:
            y_labels.remove('PS')
        if 'PA' in y_labels:
            y_labels.remove('PA')
        x_labels = ['0', '', '2000', '', '4000', '', '6000', '', '8000', '', '10000']

        peer_heatmaps = np.zeros((len(y_labels), 2000))
        sub_heatmaps = np.zeros((len(y_labels), 2000))

        for i, id in enumerate(y_labels):
            peer_heatmaps[i] = data[id][2]
            sub_heatmaps[i] = data[id][4]

        #y_labels = [''] + y_labels

        max_labels = np.round(np.linspace(45.0, 55.0, 21), 2)

        fig, ax = pyplot.subplots(dpi=600)
        ax.set_title('')
        ax.set_xlabel('Iterations')
        ax.set_ylabel('Stress Scenario')

        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)

        # Generate the pix map
        plot = ax.contourf(peer_heatmaps, cmap='bone',  vmin=45.0, vmax=50.0)#, interpolation='none')
        ax.contour(peer_heatmaps, colors = 'k',  vmin=45.0, vmax=50.0)
        cbar = fig.colorbar(plot)
        cbar.set_label('Peer Transfer %', rotation=90)
        ax.set_aspect('auto')
        fig.savefig('%s/peer_transfer_heatmap' % parser.output)
        pyplot.close(fig)

        max_labels = np.round(np.linspace(50.0, 55.0, 31), 2)

        fig, ax = pyplot.subplots(dpi=600)
        ax.set_title('')
        ax.set_xlabel('Iterations')
        ax.set_ylabel('Stress Scenario')

        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)

        # Generate the pix map
        plot = ax.contourf(sub_heatmaps, cmap='bone',  vmin=45, vmax=50.0)#, interpolation='none')
        ax.contour(sub_heatmaps, colors = 'k', vmin=45.0, vmax=50.0)
        cbar = fig.colorbar(plot)
        cbar.set_label('Sub Transfer %', rotation=90)
        ax.set_aspect('auto')
        fig.savefig('%s/sub_transfer_heatmap' % parser.output)
        pyplot.close(fig)


        attachment_heatmaps = np.zeros((len(y_labels), 2000))
        for i, id in enumerate(y_labels):
            attachment_heatmaps[i] = data[id][25]

        fig, ax = pyplot.subplots(dpi=200)
        ax.set_title('')
        ax.set_xlabel('Iterations')
        ax.set_ylabel('Stress Scenario')

        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)

        # Generate the pix map
        plot = ax.contourf(attachment_heatmaps, cmap='pink')#, interpolation='none')
        ax.contour(attachment_heatmaps, colors = 'k')
        cbar = fig.colorbar(plot)
        cbar.set_label('Attachment', rotation=90)
        ax.set_aspect('auto')
        fig.savefig('%s/attachment_heatmap' % parser.output)
        pyplot.close(fig)

        ax.set_title('')
        ax.set_xlabel('Iterations')
        ax.set_ylabel('Stress Scenario')

        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)
        pyplot.close(fig)

        fig, ax = pyplot.subplots(dpi=200)
        # Generate the pix map
        toPlot = peer_heatmaps - sub_heatmaps
        plot = ax.contourf(toPlot, cmap='summer', linewidths = 1.0)#, interpolation='none')
        ax.contour(toPlot, colors = 'k')
        cbar = fig.colorbar(plot)
        cbar.set_label('Difference (%)', rotation=90)
        ax.set_aspect('auto')
        fig.savefig('%s/difference_heatmap' % parser.output)
        pyplot.close(fig)



        toPlot = [data[a][2][1999] - data[a][4][1999] for a in y_labels]

        fig, ax = pyplot.subplots(dpi=200)
        ax.set_xlabel('Stress Scenarios')
        ax.set_ylabel('Difference (%) (Peer - Sub)')
        plot = ax.plot(y_labels, toPlot)
        ax.set_aspect('auto')
        fig.savefig('%s/difference_plot' % parser.output)
        pyplot.close(fig)

    for a in data:
        write_plot([a], '%s/transfer_chance/%s_transfer_chance' % (parser.output, a), data,
                   'Peer and Sub Transfer Properties\n for Scenario with %s stress waves.' % a,
                   [2, 4], 'Iteration', 'Probability (%)', data_types=data_types,
                   show_std=1)
        write_plot([a], '%s/transfer_difference/%s_transfer_difference' % (parser.output, a), data,
                   'Relative Change in Peer and Sub Transfer properties\n for Scenario %s' % a,
                   [6, 8], 'Iteration', '%', data_types=data_types,
                   show_std=1)

        write_plot([a], '%s/relative_prop_diff/%s_prop_difference_sgp' % (parser.output, a), data,
                   'Relative Difference in Peer and Sub Transfer properties\n for Scenario %s where Sub[0] > Peer[0]' % a,
                   [12, 14], 'Iteration', '%', data_types=data_types, show_std=1)

        write_plot([a], '%s/relative_prop_diff/%s_prop_difference_pgs' % (parser.output, a), data,
                   'Relative Difference in Peer and Sub Transfer properties\n for Scenario %s where Sub[0] < Peer[0]' % a,
                   [16, 18], 'Iteration', '%', data_types=data_types, show_std=1)

        write_plot([a], '%s/attachment/%s_attachment' % (parser.output, a), data,
                   'Evolution of Attachment Gene for Scenario %s' % a,
                   [25], 'Iteration', 'Attachment', data_types=data_types, show_std=1)

        write_plot([a], '%s/actions/%s_actions' % (parser.output, a), log_data,
                   'Number of Resource Transfer Actions\n for Scenario %s' % a,
                   [0,4], 'Iteration', 'Count', data_types={a: ['Sub', 'Peer']},
                   show_std=1, iterations=np.arange(10000))

        write_bar_plot(a, '%s/dist/%s_distribution' % (parser.output, a), bar_data[a],
                   'Final Distribution of Peer and Sub Transfer properties\n for Scenario %s' % a, 'Bins', 'Distribution (%)')

        print('%s:' % a)
        print('%s:\n0: %s\t 5000: %s\t10000: %s' % ('Peer', data[a][2][0], data[a][2][999] - data[a][2][0], data[a][2][1999] -data[a][2][0]))
        print('%s:\n0: %s\t 5000: %s\t10000: %s' % ('Sub', data[a][4][0], data[a][4][999]  - data[a][4][0], data[a][4][1999]  - data[a][4][0]))
        print('%s:\n0: %s +/- %s p:%s\t 5000: %s +/- %s p:%s\t10000: %s +/- %s p:%s' % ('Stats:', data[a][0][0], data[a][1][0], data[a][18][0],
                                                                           data[a][0][999], data[a][1][999], data[a][20][999],
                                                                           data[a][0][1999], data[a][1][1999], data[a][20][1999]))
        print('Diff: %s Ranksums: %s' % (str(data[a][2][1999] - data[a][4][1999]),str(stats.ranksums(stats_data[a][1], stats_data[a][2], alternative='greater').pvalue)))
        print()


    print("Kruskal Tests:")
    toTest = np.zeros((len(plots_ids), 50), dtype=float)
    for i, kkey in enumerate(plots_ids):
        toTest[i] = stats_data[kkey][0]

    to_compare = [toTest[i] for i in range(len(plots_ids))]
    print('Kruskal: ' + str(stats.kruskal(*to_compare).pvalue))
    print(sp.posthoc_dunn(to_compare, p_adjust = 'bonferroni'))

    print("\nFinal Peer:")


if __name__ == '__main__':
    main()