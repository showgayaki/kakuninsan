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
        created_at: 5
    """

    def __init__(self, data):
        self.data = data

    def draw_graph(self, now, current_dir):
        # グラフ画像ファイル
        now = now.strftime('%Y-%m-%d_%H-%M-%S')
        image_dir = os.path.join(Path(current_dir).resolve().parents[0], 'img')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        image_file_path = os.path.join(image_dir, '{}.png'.format(now))

        fig = plt.figure(figsize=(9, 6))
        ax = fig.add_subplot(111)

        # プロットデータ配列作成
        x = []
        y_download = []
        y_upload = []
        dt_max = ''
        for i, d in enumerate(reversed(self.data)):
            if i == len(self.data) - 1:
                dt_max = d[5].replace(minute=0, second=0) + datetime.timedelta(hours=1)
            x.append(d[5])
            download = bytes_to_megabytes(d[2])
            upload = bytes_to_megabytes(d[3])
            y_download.append(download)
            y_upload.append(upload)

        ax.plot(x, y_download, 'o-', ms=2, label='Download')
        ax.plot(x, y_upload, 'o-', ms=2, label='Upload')

        # x軸目盛り用配列作成
        interval_hour = 24
        x_axis = []
        for i in reversed(range(0, interval_hour)):
            dt = dt_max + datetime.timedelta(hours=-i)
            x_axis.append(dt)

        # x軸の目盛り
        xticks = mdates.date2num(x_axis)
        ax.set_xlim(mdates.date2num([x_axis[0], dt_max]))
        ax.xaxis.set_major_locator(mdates.ticker.FixedLocator(xticks))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%-H'))

        # グラフ装飾
        dt_min_view = '{0:%-m/%-d}'.format(x_axis[0])
        dt_max_view = '{0:%-m/%-d}'.format(dt_max)
        plt.title('Internet Speed ({} - {})'.format(dt_min_view, dt_max_view))
        plt.legend(loc='upper left', fontsize=9)
        plt.xlabel('Hour')
        plt.ylabel('Speed(Mbps)')
        plt.grid(True)

        # グラフ画像保存
        fig.savefig(image_file_path, bbox_inches="tight")

        return image_file_path if os.path.exists(image_file_path) else ''


def bytes_to_megabytes(bps):
    mega = 10 ** 6
    mbps = int(bps / mega)
    return mbps
