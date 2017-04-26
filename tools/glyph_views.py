from django.shortcuts import render
from django.http.response import Http404


SVG_ROOT = './static/svg'
svg_list = None
svg_page_num = 0
SVG_NUM_PER_PAGE=100.0

def _get_svg_list_tuple():
    from math import ceil
    from os import listdir
    from os.path import isfile, join

    global svg_list
    global svg_page_num
    if svg_list is None:
        svg_list = [f for f in listdir(SVG_ROOT) if isfile(join(SVG_ROOT, f))]
        svg_page_num = int(ceil(len(svg_list)/SVG_NUM_PER_PAGE))

    return svg_list, svg_page_num


def index(request):
    return page(request, 0)


def page(request, page_idx):
    page_idx = int(page_idx)
    svg_list, page_num = _get_svg_list_tuple()

    if page_idx >= page_num or page_idx<0:
        raise Http404

    start_idx = int(max(page_idx * SVG_NUM_PER_PAGE, 0))
    end_idx = int(min(start_idx+SVG_NUM_PER_PAGE, len(svg_list)))

    return render(request, 'glyph.html', {'pg':page_idx, 'pgNum':page_num,'svg_list':svg_list[start_idx:end_idx]})