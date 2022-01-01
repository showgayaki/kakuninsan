import os
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Graph:
    """
    [self.data]
    index:
        download: 2
        upload: 3
        created_at: 6
    """
    def __init__(self, data):
        self.data = data

    def draw_graph(self):
        fig = plt.figure(figsize=(9, 6))
        ax = fig.add_subplot(111)

        # プロットデータ配列作成
        x = []
        y_download = []
        y_upload = []
        for d in reversed(self.data):
            x.append(d[6])
            y_download.append(bytes_to_megabytes(d[2]))
            y_upload.append(bytes_to_megabytes(d[3]))

        ax.plot(x, y_download, 'o-', ms=2, label='Download')
        ax.plot(x, y_upload, 'o-', ms=2, label='Upload')

        # x軸目盛線：レコードすべてを含むように
        dt_max = self.data[0][6].replace(minute=0, second=0, microsecond=0)
        dt_min = self.data[-1][6].replace(minute=0, second=0, microsecond=0)
        x_axis = []
        i = 0
        while True:
            dt = dt_min + datetime.timedelta(hours=i)
            x_axis.append(dt)
            i += 1
            if dt == dt_max:
                x_axis.append(dt_min + datetime.timedelta(hours=i))
                break

        xticks = mdates.date2num(x_axis)
        ax.set_xlim(mdates.date2num([x_axis[0], x_axis[-1]]))
        ax.xaxis.set_major_locator(mdates.ticker.FixedLocator(xticks))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%-H'))

        # グラフ装飾
        dt_min_view = '{0:%-m/%-d}'.format(x_axis[0])
        dt_max_view = '{0:%-m/%-d}'.format(x_axis[-1])
        plt.title('Internet Speed ({} - {})'.format(dt_min_view, dt_max_view))
        plt.legend(loc='upper left', fontsize=9)
        plt.xlabel('Hour')
        plt.ylabel('Speed(Mbps)')
        plt.ylim(0,)
        plt.grid(True)

        # グラフ画像保存
        image_dir = os.path.join(Path(os.path.dirname(__file__)).parent, 'web/src/img')
        if not os.path.isdir(image_dir):
            os.makedirs(image_dir)
        image_file_path = os.path.join(image_dir, 'graph.png')
        fig.savefig(image_file_path, bbox_inches="tight")

        return image_file_path if os.path.exists(image_file_path) else ''


def bytes_to_megabytes(bps):
    mega = 10 ** 6
    mbps = int(bps / mega)
    return mbps
