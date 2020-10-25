# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from astropy.stats import biweight_scale, biweight_location
from scipy import stats
from scipy.stats import gaussian_kde
from tabulate import tabulate

import chisquare_v4 as cs

# Calculando os parâmetros
pasta = 'all'  # nome da pasta de resultados all/globular/open/cl-assoc/hl
Nsint = 2000
Ns = 3
nomes = np.loadtxt('results/photometry-' + pasta + '_cat.txt', usecols=[0], dtype=str)
fields = np.loadtxt('results/photometry-' + pasta + '_cat.txt', usecols=[1], dtype=str)
literature_param = np.loadtxt('results/parameter-cat.txt', usecols=(5, 3, 7))
literature_name = np.loadtxt('results/parameter-cat.txt', usecols=(0), dtype=str)
print(pasta)
print('Object field [Fe/H](Lit,Mode,Median,-,+) log(Age)(Lit,Mode,Median,-,+)')
for i in range(0, len(nomes)):
    cluster_locator = 0  # locating the cluster in the literature table
    while (literature_name[cluster_locator] != nomes[i]):
        cluster_locator = cluster_locator + 1

    cluster = np.loadtxt('results/photometry-' + pasta + '_cat.txt',
                         usecols=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
                                  25, 26, 27, 28])[i]

    sint_cluster = np.zeros((Nsint, 27))
    sint_cluster[0, :] = cluster
    sint_cluster_param = np.zeros((Nsint, 3))
    for k in range(1, Nsint):
        sint_cluster[k, 0:3] = cluster[0:3]
        for m in range(0, 24):
            if m < 12:
                sint_cluster[k, 3 + m] = np.random.normal(cluster[3 + m], Ns * cluster[15 + m], 1)
                # print(cluster[15+m])
            else:
                sint_cluster[k, 3 + m] = cluster[3 + m]
            if sint_cluster[k, 3 + m] < 0:
                sint_cluster[k, 3 + m] = -sint_cluster[k, 3 + m]
    # print(sint_cluster[:,3:15])
    # break
    for j in range(0, len(sint_cluster)):
        chi_ebv, chi_Z, chi_age = cs.full_fit(cs.load_table('tables/mag_full.dat'),
                                              sint_cluster, j,
                                              (['uJava', 'uJava', 'uJava', 'uJava', 'F378', 'F378', 'F430', 'gSDSS',
                                                'F660', 'F861', 'uJava']),
                                              (['F660', 'rSDSS', 'iSDSS', 'zSDSS', 'F515', 'gSDSS', 'gSDSS', 'zSDSS',
                                                'gSDSS', 'uJava', 'F515']),
                                              # cs.load_table('best5_100age.dat')[-5,0:11],
                                              np.ones(11),
                                              (['iSDSS', 'rSDSS', 'uJava', 'F378', 'F410', 'F430', 'F515', 'F660',
                                                'F660', 'gSDSS', 'iSDSS']),
                                              (['zSDSS', 'zSDSS', 'zSDSS', 'zSDSS', 'zSDSS', 'iSDSS', 'zSDSS', 'F861',
                                                'iSDSS', 'zSDSS', 'F861']),
                                              np.ones(11),
                                              # cs.load_table('best5_100Z_test6.dat')[-5,0:11])1:29
                                              (
                                                  ['F660', 'gSDSS', 'rSDSS', 'F378', 'F378', 'F410', 'F410', 'F660',
                                                   'F410',
                                                   'F378', 'iSDSS']),
                                              (['iSDSS', 'F861', 'F861', 'F395', 'gSDSS', 'F430', 'F515', 'F861',
                                                'gSDSS', 'F660', 'F861']),
                                              np.ones(11))
        # cs.load_table('best5_100Z_test6.dat')[-5,0:11])tables
        np.set_printoptions(precision=2)
        # print (nomes[i], chi_age[0:3],chi_Z[0:3],chi_ebv[0:3])

        # Ajuste com aglomerados desavermelhados, usar tabela mag1.dat (mudar no cabeçalho da função)
        # chi_Z=np.log10((chi_Z[0]/(1-chi_Z[0]-(0.2485+(1.78*chi_Z[0]))))/(0.0207)),np.log10(chi_Z[1]),chi_Z[2]
        chi_Z = np.log10(chi_Z[0] / 0.019), np.log10(chi_Z[1]), chi_Z[2]
        sint_cluster_param[j, :] = chi_Z
        # print(nomes[i],chi_Z[0:3],np.abs(chi_Z[0]-literature[cluster_locator,0]),
        # np.abs(chi_Z[1]-literature[cluster_locator,1]))

        # Ajuste com aglomerados avermelhados, usar tabela mag.dat (mudar no cabeçalho da função)
        # chi_ebv=np.log10((chi_ebv[0]/(1-chi_ebv[0]-(0.2485+(1.78*chi_ebv[0]))))/(0.0207)),np.log10(chi_ebv[1]),chi_ebv[2]
        # sint_cluster_param[j,:]=chi_ebv
        # print(nomes[i], chi_ebv[0:3], np.abs(chi_ebv[0] - literature[cluster_locator, 0]),
        # np.abs(chi_ebv[1] - literature[cluster_locator, 1]))

    np.set_printoptions(precision=2)
    # percentils de idade e metalicidade
    Z_percentiles = [np.percentile(sint_cluster_param[:, 0], 50, interpolation='nearest'),
                     np.percentile(sint_cluster_param[:, 0], 16, interpolation='nearest'),
                     np.percentile(sint_cluster_param[:, 0], 84, interpolation='nearest'),
                     float(stats.mode(sint_cluster_param[:, 0])[0])]
    age_percentiles = [np.percentile(sint_cluster_param[:, 1], 50, interpolation='nearest'),
                       np.percentile(sint_cluster_param[:, 1], 16, interpolation='nearest'),
                       np.percentile(sint_cluster_param[:, 1], 84, interpolation='nearest'),
                       float(stats.mode(sint_cluster_param[:, 1])[0])]
    # print(Z_percentiles, age_percentiles)
    print("{} {} ({:.2f} {:.2f} {:.2f} {:.2f} {:.2f}) ({:.2f} {:.2f} {:.2f} {:.2f} {:.2f})".format(nomes[i], fields[i],
                                                                                                   literature_param[
                                                                                                       cluster_locator, 0],
                                                                                                   Z_percentiles[3],
                                                                                                   Z_percentiles[0],
                                                                                                   Z_percentiles[1],
                                                                                                   Z_percentiles[2],
                                                                                                   literature_param[
                                                                                                       cluster_locator, 1],
                                                                                                   age_percentiles[3],
                                                                                                   age_percentiles[0],
                                                                                                   age_percentiles[1],
                                                                                                   age_percentiles[2]))

    if i == 0:
        with open('results/' + pasta + '/clusters_output.txt', 'w') as f:
            f.write(
                '#Object field Lit_[Fe/H] Mode_[Fe/H] Mean_[Fe/H] -_[Fe/H] +_[Fe/H] Lit_log(Age) Mode_log(Age) Median_log(Age) -_log(Age) +_log(Age) \n')
            f.write("{} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}\n".format(nomes[i],
                                                                                                           fields[i],
                                                                                                           literature_param[
                                                                                                               cluster_locator, 0],
                                                                                                           Z_percentiles[
                                                                                                               3],
                                                                                                           Z_percentiles[
                                                                                                               0],
                                                                                                           Z_percentiles[
                                                                                                               1],
                                                                                                           Z_percentiles[
                                                                                                               2],
                                                                                                           literature_param[
                                                                                                               cluster_locator, 1],
                                                                                                           age_percentiles[
                                                                                                               3],
                                                                                                           age_percentiles[
                                                                                                               0],
                                                                                                           age_percentiles[
                                                                                                               1],
                                                                                                           age_percentiles[
                                                                                                               2]))
            # f.write('{} {:.2f} {:.2f} {:.2f} {:.4f} {:.2f}\n'.format(nomes[i], chi_Z[0], chi_Z[1], chi_Z[2],
            # np.abs(chi_Z[0] - literature[i, 0]),
            # np.abs(chi_Z[1] - literature[i, 0])))
    else:
        with open('results/' + pasta + '/clusters_output.txt', 'a') as f:
            f.write("{} {} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f}\n".format(nomes[i],
                                                                                                           fields[i],
                                                                                                           literature_param[
                                                                                                               cluster_locator, 0],
                                                                                                           Z_percentiles[
                                                                                                               3],
                                                                                                           Z_percentiles[
                                                                                                               0],
                                                                                                           Z_percentiles[
                                                                                                               1],
                                                                                                           Z_percentiles[
                                                                                                               2],
                                                                                                           literature_param[
                                                                                                               cluster_locator, 1],
                                                                                                           age_percentiles[
                                                                                                               3],
                                                                                                           age_percentiles[
                                                                                                               0],
                                                                                                           age_percentiles[
                                                                                                               1],
                                                                                                           age_percentiles[
                                                                                                               2]))
            # f.write('{} {:.2f} {:.2f} {:.2f} {:.4f} {:.2f}\n'.format(nomes[i], chi_Z[0], chi_Z[1], chi_Z[2],
            #                                                        np.abs(chi_Z[0] - literature[i, 0]),
            #                                                        np.abs(chi_Z[1] - literature[i, 1])))

    # plt.subplots(3,3, constrained_layout=True)#(figsize=(12, 12))
    # plt.suptitle(fields[i]+'_'+nomes[i])
    mmm_Z = np.mean((Z_percentiles[0], Z_percentiles[3]))
    mmm_age = np.mean((age_percentiles[0], age_percentiles[3]))
    fig = plt.figure(constrained_layout=False)
    gs = fig.add_gridspec(nrows=2, ncols=2, width_ratios=[2, 1], height_ratios=[1, 2])

    # plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2)

    # plt.subplot2grid((3, 3), (1, 2), rowspan=2)
    # plt.subplot(221)
    a = fig.add_subplot(gs[1, 1])
    n, bins_Z, patches = plt.hist(sint_cluster_param[:, 0], orientation='horizontal')
    # bins=np.arange((literature_param[cluster_locator,0]-1),
    #               (literature_param[cluster_locator,0]+1),0.1),
    # orientation='horizontal')
    # print(n, bins_Z)
    a.axes.get_yaxis().set_visible(False)
    plt.hlines(literature_param[cluster_locator, 0], 0, np.max(n), label='literature', color='black', zorder=5)
    plt.hlines(Z_percentiles[3], 0, np.max(n) / 3, label='mode', color='purple', zorder=3)
    plt.hlines(Z_percentiles[0], 0, np.max(n) / 2, label='median', color='orange', zorder=2)
    plt.ylim(np.min(bins_Z) - 0.1, np.max(bins_Z) + 0.1)
    plt.hlines(mmm_Z, 0, np.max(n) / 1, label='mmm', color='blue', zorder=4)
    plt.hlines(Z_percentiles[1], 0, np.max(n) / 4, label='16%', color='red')
    plt.hlines(Z_percentiles[2], 0, np.max(n) / 4, label='84%', color='green')
    # plt.legend(bbox_to_anchor=(1.0,1.05), loc="upper left", frameon=False)
    # plt.ylabel('[Fe/H]',fontsize=15)
    plt.xlabel('N', fontsize=15)
    # plt.tick_params(labelsize=15)

    # plt.subplot2grid((3, 3), (0, 0), colspan=2)
    # plt.subplot(222)
    a = fig.add_subplot(gs[0, 0])
    n, bins_age, patches = plt.hist(sint_cluster_param[:, 1], orientation='vertical')
    # bins=np.arange((literature_param[cluster_locator,1]-1),
    #                                    (literature_param[cluster_locator,1]+1),0.1),
    #                  orientation='vertical')
    # print(n,bins_age)

    plt.vlines(literature_param[cluster_locator, 1], 0, np.max(n) / 1, label='literature', color='black', zorder=5)
    plt.vlines(age_percentiles[3], 0, np.max(n) / 3, label='mode', color='purple', zorder=3)
    plt.vlines(age_percentiles[0], 0, np.max(n) / 2, label='median', color='orange', zorder=2)
    a.axes.get_xaxis().set_visible(False)
    plt.xlim(np.min(bins_age) - 0.05, np.max(bins_age) + 0.05)
    plt.vlines(mmm_age, 0, np.max(n) / 1, label='mmm', color='blue', zorder=4)
    plt.vlines(age_percentiles[1], 0, np.max(n) / 4, label='16%', color='red')
    plt.vlines(age_percentiles[2], 0, np.max(n) / 4, label='84%', color='green')
    plt.legend(bbox_to_anchor=(1.0, 1.05), loc="upper left", frameon=False)
    # plt.xlabel('log(Age)', fontsize=15)
    plt.ylabel('N', fontsize=15)
    # plt.tick_params(labelsize=15)

    fig.add_subplot(gs[1, 0])
    plt.ylabel('[Fe/H]', fontsize=15)
    plt.xlabel('log(Age)', fontsize=15)
    plt.ylim(np.min(bins_Z) - 0.1, np.max(bins_Z) + 0.1)
    plt.xlim(np.min(bins_age) - 0.05, np.max(bins_age) + 0.05)
    d = np.vstack([sint_cluster_param[:, 1], sint_cluster_param[:, 0]])
    density = gaussian_kde(d)(d)
    sc = plt.scatter(sint_cluster_param[:, 1], sint_cluster_param[:, 0], marker='.', c=density, s=100, edgecolor='',
                     zorder=4)
    # plt.scatter(mmm_age, mmm_Z, marker='o', color='blue')
    plt.hlines(mmm_Z, np.min(bins_age) - 0.05, np.max(bins_age) + 0.05, color='blue', zorder=3)
    plt.vlines(mmm_age, np.min(bins_Z) - 0.1, np.max(bins_Z) + 0.1, color='blue', zorder=3)
    plt.scatter(literature_param[cluster_locator, 1], literature_param[cluster_locator, 0], marker='x', color='black',
                zorder=5)

    # fig.add_subplot(gs[:, 2])
    # cb = mpl.colorbar.ColorbarBase(cax, orientation='vertical')
    position = fig.add_axes([0.9, 0.02, 0.01, 0.9])
    cb = plt.colorbar(sc, cax=position, orientation='vertical', label='density of models fitted (gaussian_kde)')
    # plt.axis('off')
    fig.subplots_adjust(wspace=0, hspace=0)

    # plt.tight_layout()
    plt.savefig('results/' + pasta + '/mcmc_hists/' + fields[i] + '_' + nomes[i] + '.png',
                dpi=300)  # ,bbox_inches='tight')
    plt.close()
    # plt.show()

results_strings = np.loadtxt('results/' + pasta + '/clusters_output.txt', usecols=[0, 1], dtype=str)
results_floats = np.loadtxt('results/' + pasta + '/clusters_output.txt', usecols=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                            dtype=float)
results = np.hstack((results_strings, results_floats))

# location=[biweight_location(results_floats[:,0]-results_floats[:,1]),biweight_location(results_floats[:,5]-results_floats[:,6])]
# scale=[biweight_scale(results_floats[:,0]-results_floats[:,1]),biweight_scale(results_floats[:,5]-results_floats[:,6])]


mmm_Z = np.zeros((len(results_floats)))
mmm_age = np.zeros((len(results_floats)))

for i in range(len(results_floats)):
    mmm_Z[i] = np.mean((results_floats[i, 1], results_floats[i, 2]))
    mmm_age[i] = np.mean((results_floats[i, 6], results_floats[i, 7]))

location = [biweight_location(results_floats[:, 0] - mmm_Z),
            biweight_location(results_floats[:, 5] - mmm_age)]
scale = [biweight_scale(results_floats[:, 0] - mmm_Z),
         biweight_scale(results_floats[:, 5] - mmm_age)]
print(location[0], scale[0])
print(location[1], scale[1])

results_latex = tabulate(results, tablefmt="latex",
                         headers=["Object", "field", "Lit_[Fe/H]", "Mode_[Fe/H]", "Mean_[Fe/H]" "-_[Fe/H]",
                                  "+_[Fe/H]", "Lit_log(Age)", "Mode_log(Age)", "Mean_log(Age)", "-_log(Age)",
                                  "+_log(Age)"])

with open('results/' + pasta + '/clusters_output_latex.txt', 'w') as f:
    f.write("{}".format(results_latex))

fig0, ax0 = plt.subplots(ncols=1)
x = np.arange(0, len(results_strings))
ax0.set_xlabel('Clusters')
ax0.set_ylabel('ref_[Fe/H]-calc_[Fe/H]', fontsize=15)
ax0.set_xticks(x)
ax0.set_xticklabels((results_strings[:, 0]), rotation='vertical', fontsize=8)
# plt.tick_params(labelsize=15)

for i in range(len(results_strings)):
    ax0.scatter(i, (results_floats[i, 0] - mmm_Z[i]), marker='o')

ax0.hlines(location[0] + scale[0], 0, len(results_floats[:, 1]), label='biweight scale')
ax0.hlines(location[0] - scale[0], 0, len(results_floats[:, 1]))
ax0.hlines(location[0], 0, len(results_floats[:, 1]), color='blue', label='biweight location')
plt.legend()
plt.tight_layout()
plt.savefig('results/' + pasta + '/clusters_Z.png', dpi=300, bbox_inches='tight')

fig1, ax1 = plt.subplots(ncols=1)
# plt.subplots(121)
x = np.arange(0, len(results_strings))
ax1.set_xlabel('Clusters')
ax1.set_ylabel('ref_log(age)-calc_log(age)', fontsize=15)
ax1.set_xticks(x)
ax1.set_xticklabels(results_strings[:, 0], rotation='vertical', fontsize=8)  # adicionar campo no tick também?

for i in range(len(results_strings)):
    ax1.scatter(i, (results_floats[i, 5] - mmm_age[i]), marker='o')
    # plt.xticks(results_strings[i,1],rotation=55)
    # if(results_floats[i,2]!=results_floats[i,3]):
    #    ax1.vlines(results_strings[i,0],results_floats[i,2],results_floats[i,3])

ax1.hlines(location[1] + scale[1], 0, len(results_floats[:, 6]), label='biweight scale')
ax1.hlines(location[1] - scale[1], 0, len(results_floats[:, 6]))
ax1.hlines(location[1], 0, len(results_floats[:, 6]), color='blue', label='biweight location')

plt.legend()
plt.tight_layout()
plt.savefig('results/' + pasta + '/clusters_age.png', dpi=300, bbox_inches='tight')
# plt.show()

with open('results/' + pasta + '/clusters_output_latex.txt', 'w') as f:
    f.write("{}".format(results_latex))

fig0, ax0 = plt.subplots(ncols=1)
# x=np.arange(0,len(results_strings))
ax0.set_xlabel('ref_[Fe/H]')
ax0.set_ylabel('ref_[Fe/H]-calc_[Fe/H]', fontsize=15)
# ax0.set_xticks(x)
# ax0.set_xticklabels((results_strings[:,0]),rotation='vertical',fontsize=8)
# plt.tick_params(labelsize=15)

for i in range(len(results_strings)):
    # print(i,np.abs(results_floats[i, 0] - results_floats[i, 1]))

    ax0.scatter(results_floats[i, 0], (results_floats[i, 0] - results_floats[i, 1]), marker='o')
    # if(results_floats[i,2]!=results_floats[i,3]):
    #    ax0.vlines(results_strings[i,0],results_floats[i,2],results_floats[i,3])

ax0.hlines(location[0] + scale[0], np.min(results_floats[:, 0]), np.max(results_floats[:, 0]), label='biweight scale')
ax0.hlines(location[0] - scale[0], np.min(results_floats[:, 0]), np.max(results_floats[:, 0]))
ax0.hlines(location[0], np.min(results_floats[:, 0]), np.max(results_floats[:, 0]), color='blue',
           label='biweight location')
plt.legend()
plt.tight_layout()
plt.savefig('results/' + pasta + '/clusters_Z-error.png', dpi=300, bbox_inches='tight')

fig1, ax1 = plt.subplots(ncols=1)
# plt.subplots(121)
# x=np.arange(0,len(results_strings))
ax1.set_xlabel('ref_log(age)')
ax1.set_ylabel('ref_log(age)-calc_log(age)', fontsize=15)
# ax1.set_xticks(x)
# ax1.set_xticklabels(results_strings[:,0],rotation='vertical',fontsize=8) #adicionar campo no tick também?


for i in range(len(results_strings)):
    ax1.scatter(results_floats[i, 5], (results_floats[i, 5] - results_floats[i, 7]), marker='o')
    # plt.xticks(results_strings[i,1],rotation=55)
    # if(results_floats[i,2]!=results_floats[i,3]):
    #    ax1.vlines(results_strings[i,0],results_floats[i,2],results_floats[i,3])

ax1.hlines(location[1] + scale[1], np.min(results_floats[:, 5]), np.max(results_floats[:, 5]), label='biweight scale')
ax1.hlines(location[1] - scale[1], np.min(results_floats[:, 5]), np.max(results_floats[:, 5]))
ax1.hlines(location[1], np.min(results_floats[:, 5]), np.max(results_floats[:, 5]), color='blue',
           label='biweight location')
# plt.xlim(9,10.13)
# plt.ylim(-1,1)
plt.legend()
plt.tight_layout()
plt.savefig('results/' + pasta + '/clusters_age-error.png', dpi=300, bbox_inches='tight')
# plt.show()