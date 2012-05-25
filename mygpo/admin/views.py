import re

from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from mygpo.admin.auth import require_staff
from mygpo.admin.group import PodcastGrouper
from mygpo.core.models import Podcast
from mygpo.counter import Counter
from mygpo.maintenance.merge import PodcastMerger, IncorrectMergeException


@require_staff
def overview(request):
    return render(request, 'admin/overview.html', {
        })


@require_staff
def merge_select(request):
    return render(request, 'admin/merge-select.html', {
        })


@require_staff
def merge_verify(request):
    podcast_url1 = request.POST['feed1']
    podcast_url2 = request.POST['feed2']
    podcast1 = Podcast.for_url(podcast_url1)
    podcast2 = Podcast.for_url(podcast_url2)

    if podcast1 is None:
        messages.error(request,
                _('No podcast with URL {url}').format(url=podcast_url1))
        return HttpResponseRedirect(reverse('admin-merge'))

    if podcast2 is None:
        messages.error(request,
                _('No podcast with URL {url}').format(url=podcast_url2))
        return HttpResponseRedirect(reverse('admin-merge'))


    grouper = PodcastGrouper(podcast1, podcast2)

    get_features = lambda (e_id, e): ((e.url, e.title), e_id)

    num_groups = grouper.group(get_features)

    return render(request, 'admin/merge-grouping.html', {
            'podcast1': podcast1,
            'podcast2': podcast2,
            'groups': num_groups,
        })


RE_EPISODE = re.compile(r'episode_([0-9a-fA-F]{32})')

@require_staff
def merge_process(request):

    podcast1 = Podcast.for_url(request.POST['feed1'])
    podcast2 = Podcast.for_url(request.POST['feed2'])

    grouper = PodcastGrouper(podcast1, podcast2)

    features = {}
    for key, feature in request.POST.items():
        m = RE_EPISODE.match(key)
        if m:
            episode_id = m.group(1)
            features[episode_id] = feature

    get_features = lambda (e_id, e): (features[e_id], e_id)

    num_groups = grouper.group(get_features)

    if 'renew' in request.POST:
        return render(request, 'admin/merge-grouping.html', {
                'podcast1': podcast1,
                'podcast2': podcast2,
                'groups': num_groups,
            })


    elif 'merge' in request.POST:

        actions = Counter()

        try:
            # merge podcast, reassign episodes
            pm = PodcastMerger(podcast1, podcast2, actions, num_groups)
            pm.merge()
        except IncorrectMergeException as ime:
            messages.error(request, str(ime))
            return HttpResponseRedirect(reverse('admin-merge'))

        return render(request, 'admin/merge-finished.html', {
                'actions': actions.items(),
                'podcast': podcast1,
            })