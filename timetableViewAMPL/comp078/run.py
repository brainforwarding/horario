import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.sparse

from constants import *


def prepare_data(data_path):
    with open(data_path, 'r') as dsf:
        # generates a 2D data frame from the dataset using pandas
        ds_frame = dsf.read()
        ds_frame = pd.DataFrame([l.split() for l in ds_frame.split('\n')])

        # converts the data frame to a numpy 2d array and omit redundant columns
        ds_tmp = np.asarray(ds_frame)[: -1, 1: -1]

        # generate list of redundant rows indices
        redundant_rows = np.array([[i, i + 1, i + 2] for i in range(-1, ds_tmp.shape[0], 18)]).flatten()[1:]

        # remove obtained rows from the array
        ds_tmp = (np.delete(ds_tmp, redundant_rows, 0))

        # convert to integer from string
        ds_tmp = ds_tmp.astype(int)

        # Strings with zeroes. The length 20 since we got 5 days with 4 time periods each
        ds = np.zeros((numOfCourses, numOfRooms, 20))

        # The output from AMPL is in the form of a large matrix.This matrix is
        #  here rewritten to a three - dimensional tensor.This is done for X, Y and Z.
        # will then contain sub-matrices representing all the time-periods.
        for i in range(19):
            ds[:, :, i] = ds_tmp[numOfCourses * i: numOfCourses * (i + 1), :]

        return ds

def draw_timetable(periods, days):
    f, axs = plt.subplots(len(periods), len(days))
    f.subplots_adjust(hspace=0)
    f.subplots_adjust(wspace=0)

    for n, day in enumerate(days):
        axs[0][n].set_title(day, weight='demibold')

    for n, period in enumerate(periods):
        axs[n][0].text(-0.15, 0.5, period,
                    va='center',
                    ha='right',
                    fontsize=11, weight='demibold')

    for period, day_row in enumerate(axs):
        for day, cell in enumerate(day_row):
            cell.set_xticks([])
            cell.set_yticks([])

    return axs

def plot_courses(desired_courses=[]):
    # draw the empty timetable
    cells = draw_timetable(['8:00', '10:00', '13:15', '15:15'],
                           ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])

    y_offset = .12 if not desired_courses else .16
    coursecol = coursecol1 if not desired_courses else coursecol2

    # Loop through all time periods
    for k in range(20):
        y_disp = 0
        # Find which day we are at
        day = int(np.ceil((k + 1) / 4) - 1)

        # Find which period we are at
        period = int(np.mod(k, 4))

        # print((day, period))
        # continue

        for ds, course_codes in [(x, lectures), (y, exercises), (z, comlabs)]:
            # Choose one time period at each iteration and
            # find the non-zero indexes from this matrix
            a = scipy.sparse.csc_matrix(ds[:, :, k])  # todo: maybe csr

            # i and j are vectors with the indexes
            i, j = np.nonzero(a)

            if i.shape[0] != 0:
                for ii, ij in zip(list(i), list(j)):
                    if not desired_courses or ii in desired_courses:
                        cells[period][day].text(.5, .92 - y_disp,
                                                '{}  ---  {}'.format(course_codes[ii], rooms[ij]),
                                                va='center',
                                                ha='center',
                                                fontsize=9,
                                                bbox=dict(boxstyle="round",
                                                          ec=coursecol[ii],
                                                          fc=coursecol[ii],
                                                          )
                                                )
                        y_disp += y_offset

    if desired_courses:
        cells[0][0].text(.4, .8, 'Color 1:', va='center', ha='center', fontsize=9)
        cells[0][0].text(.4, .6, 'Color 2:', va='center', ha='center', fontsize=9)
        cells[0][0].text(.6, .8,
                         '     ', va='center', ha='center', fontsize=9,
                         bbox=dict(boxstyle="round", ec=color1, fc=color1)
                         )
        cells[0][0].text(.6, .6,
                         '     ', va='center', ha='center', fontsize=9,
                         bbox=dict(boxstyle="round", ec=color2, fc=color2)
                         )


if __name__ == '__main__':
    # Getting AMPL data, that is lectures(x), exercises(y) and computer labs(z).
    x = prepare_data('ds/x.txt')
    y = prepare_data('ds/y.txt')
    z = prepare_data('ds/z.txt')

    plot_courses()

    # NOTICE: indices start from 0
    plot_courses(desired_courses=[3, 14, 4, 12])

    # shows the final plot
    plt.show()