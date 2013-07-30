#   Copyright 2013 Matthew Shanker
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import matplotlib.pyplot as plt

import plotandscheme

def decorate_gold():
    plt.legend(fontsize='x-small', frameon=False, loc='upper left')
    plt.xlabel('Time(s)')
    plt.ylabel('Gold')
    ax = plt.gca()
    ax.grid()
    #ax.set_axis_bgcolor('#DDDDDD')


def decorate_event():
    plt.xlim(xmin=0)
    plt.ylim( 0, 5.5 )

    # deaths
    plt.axhspan(0.75, 1.25, alpha=0.5, color='r')
    # items
    plt.axhspan(1.75, 2.25, alpha=0.5, color='g')
    # levels
    plt.axhspan(2.75, 3.25, alpha=0.5, color='c')

    plt.gca().get_yaxis().set_visible(False)

