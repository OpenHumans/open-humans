import json
import sys

STUDIES = ['american_gut', 'pgp', 'wildlife']
ACTIVITIES = ['data_selfie', 'runkeeper', 'twenty_three_and_me']
SOURCES = STUDIES + ACTIVITIES

with open(sys.argv[1]) as f:
    data = json.load(f)


def counts_for_sourcelist_and_threshold(sourcelist, threshold):
    return {
        'is_connected': len(
            [
                u
                for u in data
                if len([s for s in sourcelist if data[u][s]['is_connected']])
                >= threshold
            ]
        ),
        'has_files': len(
            [
                u
                for u in data
                if len([s for s in sourcelist if data[u][s]['has_files']]) >= threshold
            ]
        ),
        'is_shared': len(
            [
                u
                for u in data
                if len(
                    [
                        s
                        for s in sourcelist
                        if data[u][s]['shared_directly'] or data[u][s]['is_public']
                    ]
                )
                >= threshold
            ]
        ),
        'is_public': len(
            [
                u
                for u in data
                if len([s for s in sourcelist if data[u][s]['is_public']]) >= threshold
            ]
        ),
    }


def main():
    for u in data:
        try:
            data[u]['data_selfie']['is_connected'] = data[u]['data_selfie']['has_files']
        except KeyError:
            continue

    # Make this robust to analyzing past data dumps that didn't have all sources.
    studies = [s for s in STUDIES if s in data[data.keys()[0]]]
    sources = [s for s in SOURCES if s in data[data.keys()[0]]]

    study_twoplus_counts = counts_for_sourcelist_and_threshold(studies, 2)

    print(
        'Members that have 2+ studies...\n'
        '  ...connected: {}\n'
        '  ...with files: {}\n'
        '  ...shared: {}\n'
        '  ...public: {}\n'.format(
            *[
                study_twoplus_counts[k]
                for k in ['is_connected', 'has_files', 'is_shared', 'is_public']
            ]
        )
    )

    source_twoplus_counts = counts_for_sourcelist_and_threshold(sources, 2)

    print(
        'Members that have 2+ sources...\n'
        '  ...connected: {}\n'
        '  ...with files: {}\n'
        '  ...shared: {}\n'
        '  ...public: {}\n'.format(
            *[
                source_twoplus_counts[k]
                for k in ['is_connected', 'has_files', 'is_shared', 'is_public']
            ]
        )
    )

    study_oneplus_counts = counts_for_sourcelist_and_threshold(studies, 1)

    print(
        'Members that have 1+ studies...\n'
        '  ...connected: {}\n'
        '  ...with files: {}\n'
        '  ...shared: {}\n'
        '  ...public: {}\n'.format(
            *[
                study_oneplus_counts[k]
                for k in ['is_connected', 'has_files', 'is_shared', 'is_public']
            ]
        )
    )

    source_oneplus_counts = counts_for_sourcelist_and_threshold(sources, 1)

    print(
        'Members that have 1+ sources...\n'
        '  ...connected: {}\n'
        '  ...with files: {}\n'
        '  ...shared: {}\n'
        '  ...public: {}\n'.format(
            *[
                source_oneplus_counts[k]
                for k in ['is_connected', 'has_files', 'is_shared', 'is_public']
            ]
        )
    )

    print(
        'Members that joined Public Data Sharing:'
        ' {}'.format(len([u for u in data if data[u]['public_data_participant']]))
    )

    print(
        'Members with email unverified:'
        ' {}'.format(len([u for u in data if not data[u]['email_verified']]))
    )

    print(
        'Members with 1+ sources connected, but email unverified:'
        ' {}'.format(
            len(
                [
                    u
                    for u in data
                    if len([s for s in sources if data[u][s]['is_connected']]) >= 1
                    and not data[u]['email_verified']
                ]
            )
        )
    )


if __name__ == '__main__':
    main()
