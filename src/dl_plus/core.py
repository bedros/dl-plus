import importlib

from . import ytdl
from .exceptions import DLPlusException
from .extractor.machinery import load_all_extractors, load_extractors_by_peqn


def get_ie_name(ie_cls):
    ie_name = ie_cls.IE_NAME
    if isinstance(ie_name, property):
        return ie_cls().IE_NAME
    return ie_name


def enable_extractors(names):
    ytdl_extractor_module = ytdl.import_module('extractor')
    ytdl_extractors = ytdl_extractor_module._ALL_CLASSES
    ytdl_ie_name_cls_map = {
        get_ie_name(ie_cls): ie_cls for ie_cls in ytdl_extractors}
    generic_extractor = ytdl_extractors[-1]
    append_generic_extractor = False
    enabled_extractors = []
    for name in names:
        if name == ':builtins:':
            extractors = ytdl_extractors[:-1]
            append_generic_extractor = True
        elif name == ':plugins:':
            extractors = load_all_extractors()
        elif '/' in name:
            extractors = load_extractors_by_peqn(name)
        else:
            try:
                extractors = [ytdl_ie_name_cls_map[name]]
            except KeyError:
                raise DLPlusException(f'unknown built-in extractor: {name}')
        enabled_extractors.extend(extractors)
    if append_generic_extractor:
        enabled_extractors.append(generic_extractor)
    ie_key_cls_map = {
        extractor.ie_key(): extractor for extractor in enabled_extractors}
    ytdl_extractor_module.gen_extractor_classes = lambda: enabled_extractors
    ytdl_extractor_module.get_info_extractor = (
        lambda ie_key: ie_key_cls_map[ie_key])
    importlib.reload(ytdl.import_module('YoutubeDL'))
