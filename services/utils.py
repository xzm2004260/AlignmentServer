from datetime import datetime


def update_filename(instance, filename):
    return 'lyrics/{}'.format(datetime.now().strftime("%Y%m%d-%H%M%S"))
