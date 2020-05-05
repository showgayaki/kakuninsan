import os
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Graph:
    """
    download: 2
    upload: 3
    created_at: 5
    """
    def __init__(self, data):
        self.data = data

    def draw_graph(self, now, current_dir):
        now = now.strftime('%Y-%m-%d_%H-%M-%S')
        image_dir = os.path.join(Path(current_dir).resolve().parents[0], 'img')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        image_file_path = os.path.join(image_dir, '{}.png'.format(now))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        x = []
        y_download = []
        y_upload = []
        for i, d in enumerate(reversed(self.data)):
            if i == 0:
                dt_min = d[5]
            else:
                dt_max = d[5]
            x.append(d[5])
            download = bytes_to_megabytes(d[2])
            upload = bytes_to_megabytes(d[3])
            y_download.append(download)
            y_upload.append(upload)

        plt.title('Internet Speed')
        plt.xlabel('Datetime')
        plt.xticks(rotation=45)
        plt.ylabel('Speed(Mbps)')

        xticks = mdates.date2num([dt_min, dt_max])
        ax.xaxis.set_major_locator(mdates.ticker.FixedLocator(xticks))
        # ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=None, interval=7, tz=None))
        ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0, 24, 1), tz=None))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

        ax.plot(x, y_download, 'o-', ms=2, label='Download')
        # plt.plot(x, y_upload, label='Upload')
        plt.legend(loc='upper left', fontsize=9)
        fig.savefig(image_file_path, bbox_inches="tight")
        return False


def bytes_to_megabytes(bps):
    mega = 10 ** 6
    mbps = int(bps / mega)
    return mbps
