import logging
import os
from typing import Dict, List

from background_parser.aggregators import (FilesStatisticAggregator,
                                           FolderStatisticAggregator)
from background_parser.file_analyzer import FileAnalyzer
from background_parser.models import DirectoryStatistic, FileStatistic
from background_parser.walker import get_walker
from background_task import background


def check_difference_in_structure(folder: str, extensions: List[str]):
    """
    Returns True if there is a change in directory structure.
    :param str folder: Folder path.
    :param str extensions: File path.
    :return: True if there is any change in directory structure.
    :rtype: bool
    """
    old_files = set([f['file'] for f in list(
        FileStatistic.objects.values("file"))])
    old_dirs = set([f['directory_name'] for f in list(
        DirectoryStatistic.objects.values("directory_name"))])

    new_files = set()
    new_dirs = set()

    for path, folders, files in get_walker(folder, extensions):
        new_files.update([os.path.join(path, f) for f in files])
        new_dirs.update([os.path.join(path, d) for d in folders])
    new_dirs.update(".")
    return new_files != old_files or new_dirs != old_dirs


@background(schedule=1)
def analyze_folder_and_save_results(
        base_path: str,
        file_extensions: List[str]):
    """
    Analyzes directory with all subdirectories in all criteria.
    Also saves statistics to data base.
    :param List file_extensions:
    :param str base_path:
    :return: folder statistic
    :rtype: FolderStatisticAggregator
    """
    stats: Dict[str, FolderStatisticAggregator] = {}
    logger = logging.getLogger(__name__)

    if not check_difference_in_structure(base_path, file_extensions):
        logger.info("Nothing has changed in the structure")
        return

    base_folder_stat = None

    for path, folders, files in get_walker(base_path, file_extensions):

        # We are iterating bottom-up, it means that if the
        # folder has sub-folders, their statistic is already
        # collected and stored under this folder's key.
        folder_stat = stats.pop(path) if folders else \
            FolderStatisticAggregator()

        # calculate stats for files
        files_stat = FilesStatisticAggregator(
            files=[FileAnalyzer(os.path.join(path, f)) for f in files]
        ).calculate_and_aggregate_statistic()

        # adding files statistic
        folder_stat.add_files_statistic(files_stat)
        folder_stat.add_files_and_folders_info(
            [os.path.join(path, f) for f in files],
            [os.path.join(path, f) for f in folders]
        )

        folder_stat.save_stat(path)
        if path == base_path:
            base_folder_stat = folder_stat

        # merge our statistic with statistic of a parent
        parent, _ = os.path.split(path)

        if parent not in stats:

            # The check is needed if the parent exists, if not that
            # it's the first sub-folder which tries to merge it's
            # statistic, FolderStatisticAggregator should be created
            # first.

            stats[parent] = FolderStatisticAggregator()

        # добавляем нашу статистику в статистику родителя
        stats[parent].add_children_folder_stat(folder_stat)

    logger.info("Finished background task!")
    return base_folder_stat.get_stat()
