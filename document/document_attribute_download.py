import os

import requests

from repository import headers
from utils import csv_reader, csv_writer

all_graphql = '''
query {
    repository(owner:"{1}", name:"{2}") {
        defaultBranchRef {
            target {
                ... on Commit {
                    commitCount2018: history(since: "2018-01-01T00:00:00Z", until: "2018-12-31T23:59:59Z") {
                        totalCount
                    }
                    commitCount2019: history(since: "2019-01-01T00:00:00Z", until: "2019-12-31T23:59:59Z") {
                        totalCount
                    }
                    commitCount2020: history(since: "2020-01-01T00:00:00Z", until: "2020-12-31T23:59:59Z") {
                        totalCount
                    }
                    commitCount2021: history(since: "2021-01-01T00:00:00Z", until: "2021-12-31T23:59:59Z") {
                        totalCount
                    }
                    commitCount2022: history(since: "2022-01-01T00:00:00Z", until: "2022-12-31T23:59:59Z") {
                        totalCount
                    }
                }
            }
        }
        stargazers {
            totalCount
        }
        languages(first:100) {
            edges {
                node {
                    name
                }
            }
        }
    }
    issueCount2018: search(query:"repo:{3} is:issue created:2018-01-01T00:00:00Z..2018-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueCount2019: search(query:"repo:{3} is:issue created:2019-01-01T00:00:00Z..2019-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueCount2020: search(query:"repo:{3} is:issue created:2020-01-01T00:00:00Z..2020-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueCount2021: search(query:"repo:{3} is:issue created:2021-01-01T00:00:00Z..2021-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueCount2022: search(query:"repo:{3} is:issue created:2022-01-01T00:00:00Z..2022-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2018: search(query:"repo:{3} is:issue closed:2018-01-01T00:00:00Z..2018-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2019: search(query:"repo:{3} is:issue closed:2019-01-01T00:00:00Z..2019-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2020: search(query:"repo:{3} is:issue closed:2020-01-01T00:00:00Z..2020-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2021: search(query:"repo:{3} is:issue closed:2021-01-01T00:00:00Z..2021-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2022: search(query:"repo:{3} is:issue closed:2022-01-01T00:00:00Z..2022-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
}
'''

committer_graphql = '''
query {
    repository(owner:"{1}", name:"{2}") {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first:100, since:"{3}-01-01T00:00:00Z", until:"{3}-12-31T23:59:59Z"{AFTER}) {
                        totalCount
                        edges {
                            node {
                                author {
                                    email
                                }
                            }
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        }
    }
}
'''

issue_graphql = '''
query {
    repository(owner: "{1}", name: "{2}") {
        issues(first: 100{AFTER}) {
            totalCount
            edges {
                node {
                    createdAt
                    state
                    title
                    bodyText
                    comments(first: 100) {
                        edges {
                            node {
                                createdAt
                                bodyText
                            }
                        }
                    }
                }
            }
            pageInfo {
                endCursor
                hasNextPage
            }            
        }
    }
}
'''


path_programming_language = '/data/repository/languages/edges'
path_number_of_stars = '/data/repository/stargazers/totalCount'
path_commit_count_2018 = '/data/repository/defaultBranchRef/target/commitCount2018/totalCount'
path_commit_count_2019 = '/data/repository/defaultBranchRef/target/commitCount2019/totalCount'
path_commit_count_2020 = '/data/repository/defaultBranchRef/target/commitCount2020/totalCount'
path_commit_count_2021 = '/data/repository/defaultBranchRef/target/commitCount2021/totalCount'
path_commit_count_2022 = '/data/repository/defaultBranchRef/target/commitCount2022/totalCount'
path_issue_count_2018 = '/data/issueCount2018/issueCount'
path_issue_count_2019 = '/data/issueCount2019/issueCount'
path_issue_count_2020 = '/data/issueCount2020/issueCount'
path_issue_count_2021 = '/data/issueCount2021/issueCount'
path_issue_count_2022 = '/data/issueCount2022/issueCount'
path_issue_closed_count_2018 = '/data/issueClosedCount2018/issueCount'
path_issue_closed_count_2019 = '/data/issueClosedCount2019/issueCount'
path_issue_closed_count_2020 = '/data/issueClosedCount2020/issueCount'
path_issue_closed_count_2021 = '/data/issueClosedCount2021/issueCount'
path_issue_closed_count_2022 = '/data/issueClosedCount2022/issueCount'

path_committer_list = '/data/repository/defaultBranchRef/target/history/edges'
path_committer_count = '/data/repository/defaultBranchRef/target/history/totalCount'
path_committer_next_page = '/data/repository/defaultBranchRef/target/history/pageInfo/hasNextPage'
path_committer_cursor = '/data/repository/defaultBranchRef/target/history/pageInfo/endCursor'

path_issue_list = '/data/repository/issues/edges'
path_issue_count = '/data/repository/issues/totalCount'
path_issue_next_page = '/data/repository/issues/pageInfo/hasNextPage'
path_issue_cursor = '/data/repository/issues/pageInfo/endCursor'

def post_graphql(graphql):
    return requests.post('https://api.github.com/graphql', json={'query': graphql}, headers=headers).json()


def parse_result_dict(all_set, current_depth, path, data, result_dict):
    current_set = set(filter(lambda x: x[0] == current_depth, all_set))
    if len(all_set) > 0:
        for _, name in current_set:
            if current_depth == 0:
                name = 'data'
            if data.__class__ is dict and name in data:
                parse_result_dict(all_set - current_set, current_depth + 1, path + '/' + name, data[name], result_dict)
            elif '...' in name:
                parse_result_dict(all_set - current_set, current_depth + 1, path, data, result_dict)
            elif data.__class__ is not dict:
                result_dict[path] = data
    else:
        result_dict[path] = data


def get_names(graphql, start_index, end_index):
    names = []
    for name in graphql[start_index:end_index].split('\n'):
        name = name.strip()
        name_length = len(name)
        if name_length > 0:
            for index in range(name_length):
                if name[index] == '(' or name[index] == ':':
                    name = name[:index]
                    break
            names.append(name)
    return names


def get_result_dict(graphql, data):
    result_dict = dict()
    name_set = set()
    graphql_length = len(graphql)
    if graphql_length > 0:
        depth = 0
        start_index = 1
        for index in range(graphql_length):
            if graphql[index] == '{':
                for name in get_names(graphql, start_index, index):
                    name_set.add((depth, name))
                depth = depth + 1
                start_index = index + 1
            elif graphql[index] == '}':
                for name in get_names(graphql, start_index, index):
                    name_set.add((depth, name))
                depth = depth - 1
                start_index = index + 1
        parse_result_dict(name_set, 0, '', data, result_dict)
    return result_dict


def get_csv_rows(csv_file_path):
    rows = []
    for row in csv_reader(csv_file_path):
        rows.append(row)
    return rows


def is_exists(repo, rows):
    exists = False
    for row in rows:
        if row[0] == repo:
            exists = True
            break
    return exists


def get_list(graphql, path_list, path_next_page, path_cursor, path_count=None):
    list = []
    next_page = True
    cursor = ''
    count = None
    while next_page:
        next_graphql = graphql.replace('{AFTER}', cursor)
        # print(next_graphql)
        result_dict = get_result_dict(next_graphql, post_graphql(next_graphql))
        if path_list in result_dict:
            sub_list = result_dict[path_list]
            if path_count is not None:
                if count is None:
                    count = result_dict[path_count]
                count = count - len(sub_list)
                print(f'{count}')
            list.extend(sub_list)
            next_page = result_dict[path_next_page]
            cursor = f', after:"{result_dict[path_cursor]}"'
        else:
            next_page = False
    return list


def extract(key, dict):
    if key in dict:
        value = dict[key]
    else:
        value = None
    return value


def download_attributes(repo):
    slices = repo.split('/')
    owner = slices[0]
    project = slices[1]
    # if not is_exists(repo, language_csv_file_rows) or True:
    graphql = all_graphql.replace('{1}', owner).replace('{2}', project).replace('{3}', repo)
    result_dict = get_result_dict(graphql, post_graphql(graphql))
    programming_languages = extract(path_programming_language, result_dict)
    if programming_languages is not None:
        programming_languages = list(map(lambda x: x['node']['name'], programming_languages))
    row = [
        repo,
        extract(path_number_of_stars, result_dict),
        extract(path_commit_count_2018, result_dict),
        extract(path_commit_count_2019, result_dict),
        extract(path_commit_count_2020, result_dict),
        extract(path_commit_count_2021, result_dict),
        extract(path_commit_count_2022, result_dict),
        extract(path_issue_count_2018, result_dict),
        extract(path_issue_count_2019, result_dict),
        extract(path_issue_count_2020, result_dict),
        extract(path_issue_count_2021, result_dict),
        extract(path_issue_count_2022, result_dict),
        extract(path_issue_closed_count_2018, result_dict),
        extract(path_issue_closed_count_2019, result_dict),
        extract(path_issue_closed_count_2020, result_dict),
        extract(path_issue_closed_count_2021, result_dict),
        extract(path_issue_closed_count_2022, result_dict),
        f'{programming_languages}'
    ]
    return row


count_dict = dict()

def prepare_count_dict():
    # count_dict = dict()
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\repo_issue_counts.txt'):
        if row[1] != 'failed':
            count = int(row[1])
        else:
            count = None
        if count is not None:
            count_dict[row[0]] = count


def number_of_issues_in_file(file_path):
    number_of_issues = 0
    if os.path.exists(file_path):
        with open(file_path, encoding='utf-8') as f:
            number_of_issues = len(eval(f.readlines()[0]))
        f.close()
    return number_of_issues


def download_issues(repo):
    slices = repo.split('/')
    owner = slices[0]
    project = slices[1]
    graphql = issue_graphql.replace('{1}', owner).replace('{2}', project)
    directory_path = 'C:\\Files\\issues\\'
    file_name = repo.replace('/', '_')
    file_path = f'{directory_path}{file_name}.txt'
    if repo in count_dict:
        expected_number_of_issues = count_dict[repo]
        number_of_issues = number_of_issues_in_file(file_path)
        if expected_number_of_issues <= 5000:
            while number_of_issues < expected_number_of_issues:
                print(f'{repo} {expected_number_of_issues} {number_of_issues}')
                issue_list = get_list(graphql, path_issue_list, path_issue_next_page, path_issue_cursor, path_issue_count)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f'{issue_list}')
                number_of_issues = len(issue_list)


def repos(function):
    directory_path = 'C:\\Files\\a1\\'
    for file_name in os.listdir(directory_path):
        repo = file_name.replace('.csv', '').replace('_', '/', 1)
        function(repo)


def dummy(repo):
    file_name = repo.replace('/', '_')
    if f'{file_name}.txt' not in e_list:
        return
    slices = repo.split('/')
    owner = slices[0]
    project = slices[1]
    graphql = issue_graphql.replace('{1}', owner).replace('{2}', project).replace('{AFTER}', '')
    result_dict = get_result_dict(graphql, post_graphql(graphql))
    if path_issue_count in result_dict:
        print(f'{repo},{result_dict[path_issue_count]}')
    else:
        print(f'{repo},failed')


e_list = [
'adguardteam/adguardhome',
'airbnb/javascript',
'AlaSQL/alasql',
'ampache/ampache',
'angular/angularfire',
'angular/universal',
'angular/zone.js',
'ant-design/ant-design-mobile',
'apollographql/apollo-client',
'apollographql/apollo-server',
'aptos-labs/aptos-core',
'ardatan/graphql-tools',
'arduino/arduino-cli',
'asdf-vm/asdf',
'assimp/assimp',
'auth0/nextjs-auth0',
'authelia/authelia',
'aws-amplify/aws-sdk-android',
'aws-amplify/aws-sdk-ios',
'aws/amazon-freertos',
'aws/aws-cli',
'aws/aws-sdk-js-v3',
'aws/aws-sdk-js',
'aws/aws-sdk-php',
'aws/karpenter',
'AzureAD/microsoft-authentication-library-for-js',
'Azure/acs-engine',
'Azure/Azure-Sentinel',
'backstage/backstage',
'barryvdh/laravel-debugbar',
'beefproject/beef',
'beetbox/beets',
'behdad/harfbuzz',
'bettercap/bettercap',
'bigbluebutton/greenlight',
'biopython/biopython',
'bitcoin-core/secp256k1',
'blackmagic-debug/blackmagic',
'bnb-chain/bsc',
'bootstrap-vue/bootstrap-vue',
'boto/boto3',
'brefphp/bref',
'bridgecrewio/checkov',
'browserify/browserify',
'btcpayserver/btcpayserver',
'bytecodealliance/wasmtime',
'cacti/cacti',
'caddyserver/caddy',
'cake-build/cake',
'calcom/cal.com',
'camunda/camunda-modeler',
'caprover/caprover',
'catchorg/Catch2',
'celery/celery',
'celery/kombu',
'cert-manager/cert-manager',
'channelcat/sanic',
'chaos-mesh/chaos-mesh',
'checkstyle/checkstyle',
'chef/chef',
'Chia-Network/chia-blockchain',
'ChilliCream/graphql-platform',
'chjj/marked',
'chocobozzz/peertube',
'chocolatey/choco',
'cisco-talos/clamav-devel',
'citusdata/citus',
'clasp-developers/clasp',
'clientio/joint',
'cli/cli',
'ClosedXML/ClosedXML',
'cloudflare/wrangler-legacy',
'cloudfoundry/bosh',
'cloudfoundry/cloud_controller_ng',
'cloudfoundry/uaa',
'cobbler/cobbler',
'code-charity/youtube',
'codeigniter4/codeigniter4',
'coder/coder',
'collaboraonline/online',
'common-workflow-language/common-workflow-language',
'concourse/concourse',
'containerd/containerd',
'containers/buildah',
'containers/crun',
'containers/image',
'containers/skopeo',
'containrrr/watchtower',
'contour-terminal/contour',
'coredns/coredns',
'coreos/fleet',
'coreruleset/coreruleset',
'corona-warn-app/cwa-app-ios',
'cortexproject/cortex',
'crankyoldgit/IRremoteESP8266',
'cri-o/cri-o',
'crossplane/crossplane',
'ctz/rustls',
'curl/curl',
'cvat-ai/cvat',
'dani-garcia/vaultwarden',
'darkreader/darkreader',
'dask/dask',
'dask/distributed',
'datafuselabs/databend',
'dbeaver/cloudbeaver',
'decidim/decidim',
'deepmind/mujoco',
'dequelabs/axe-core',
'detekt/detekt',
'determined-ai/determined',
'dexidp/dex',
'dexie/dexie.js',
'diaspora/diaspora',
'diygod/rsshub',
'django/channels',
'dnnsoftware/dnn.platform',
'docarray/docarray',
'docsifyjs/docsify',
'doctrine/dbal',
'doorkeeper-gem/doorkeeper',
'dosco/graphjin',
'dotnet/command-line-api',
'dotnet/corefxlab',
'dotnet/machinelearning',
'dotnet/Nerdbank.GitVersioning',
'dotnet/Open-XML-SDK',
'dromara/hutool',
'dropwizard/dropwizard',
'dubzzz/fast-check',
'e107inc/e107',
'eclipse-ee4j/jersey',
'eclipse/jetty.project',
'eclipse/mosquitto',
'eclipse/rdf4j',
'eclipse/xtext-xtend',
'EddieHubCommunity/LinkFree',
'edx/edx-platform',
'EFForg/https-everywhere',
'EFForg/privacybadger',
'elabftw/elabftw',
'elastic/ansible-elasticsearch',
'elastic/curator',
'elastic/elasticsearch-hadoop',
'elastic/elasticsearch-net',
'elastic/eui',
'elementsproject/lightning',
'elves/elvish',
'encode/django-rest-framework',
'encode/uvicorn',
'enso-org/enso',
'esapi/esapi-java-legacy',
'eslint/espree',
'esl/mongooseim',
'espanso/espanso',
'espruino/espruino',
'ethereum-optimism/optimism',
'ethereum/consensus-specs',
'eventlet/eventlet',
'ever-co/ever-gauzy',
'external-secrets/external-secrets',
'facebookincubator/velox',
'facebookresearch/fairscale',
'facebookresearch/fairseq',
'facebookresearch/faiss',
'facebookresearch/hydra',
'facebookresearch/mmf',
'facebookresearch/parlai',
'facebookresearch/xformers',
'facebook/buck',
'facebook/docusaurus',
'facebook/facebook-android-sdk',
'facebook/flipper',
'facebook/idb',
'facebook/litho',
'facebook/mysql-5.6',
'facebook/nuclide',
'facebook/redex',
'facebook/rocksdb',
'facebook/sapling',
'fairlearn/fairlearn',
'falcosecurity/falco',
'fasterxml/jackson-databind',
'fastify/fast-json-stringify',
'fb55/htmlparser2',
'fermyon/spin',
'FerretDB/FerretDB',
'filebrowser/filebrowser',
'filecoin-project/lotus',
'filecoin-project/venus',
'firecracker-microvm/firecracker',
'firezone/firezone',
'flarum/core',
'flarum/framework',
'flatpak/flatpak',
'floating-ui/floating-ui',
'fluent/fluentd',
'flutter/flutter-intellij',
'flutter/website',
'fluxcd/flux',
'fluxcd/flux2',
'FoalTS/foal',
'forkcms/forkcms',
'forwardemail/free-email-forwarding',
'frappe/frappe',
'freecad/freecad',
'freeCodeCamp/devdocs',
'freeCodeCamp/mail-for-good',
'freedomofpress/securedrop',
'freerdp/freerdp',
'freshrss/freshrss',
'fyne-io/fyne',
'garden-io/garden',
'gardener/gardener',
'geonode/geonode',
'getgrav/grav',
'getkirby/kirby',
'getredash/redash',
'getsentry/raven-ruby',
'getsentry/self-hosted',
'getsentry/sentry-javascript',
'getsentry/sentry-laravel',
'getsentry/sentry-php',
'getsentry/sentry-react-native',
'gitblit/gitblit',
'github/codeql',
'github/docs',
'github/fetch',
'github/hub',
'github/secure_headers',
'gitpython-developers/gitpython',
'GitTools/GitVersion',
'glacambre/firenvim',
'globalizejs/globalize',
'goauthentik/authentik',
'gocd/gocd',
'gocodebox/lifterlms',
'googleapis/google-api-nodejs-client',
'googleapis/google-api-php-client',
'googleapis/google-api-python-client',
'googleapis/google-cloud-go',
'googleapis/google-cloud-python',
'GoogleCloudPlatform/python-docs-samples',
'GoogleCloudPlatform/terraformer',
'GoogleContainerTools/distroless',
'googlecontainertools/jib',
'GoogleContainerTools/kaniko',
'GoogleContainerTools/skaffold',
'googleforgames/agones',
'google/accompanist',
'google/auto',
'google/closure-compiler',
'google/error-prone',
'google/flatbuffers',
'google/glog',
'google/go-containerregistry',
'google/go-github',
'google/googletest',
'google/guava',
'google/gvisor',
'google/jax',
'google/material-design-lite',
'google/mediapipe',
'google/model-viewer',
'google/or-tools',
'google/oss-fuzz',
'google/re2',
'google/sanitizers',
'google/sentencepiece',
'google/traceur-compiler',
'google/web-starter-kit',
'google/yapf',
'gophish/gophish',
'goreleaser/goreleaser',
'gpac/gpac',
'gradio-app/gradio',
'grafana/agent',
'grafana/k6',
'grafana/mimir',
'grafana/oncall',
'graphql/graphiql',
'grocy/grocy',
'grpc/grpc-java',
'gruntjs/grunt',
'gsliepen/tinc',
'guzzle/guzzle',
'Hacker0x01/react-datepicker',
'halo-dev/halo',
'HandBrake/HandBrake',
'hangfireio/hangfire',
'hapijs/hapi',
'hapijs/joi',
'haraldk/twelvemonkeys',
'harfbuzz/harfbuzz',
'harmony-one/harmony',
'harttle/liquidjs',
'hashicorp/terraform-cdk',
'hay-kot/mealie',
'hestiacp/hestiacp',
'highlightjs/highlight.js',
'honestbleeps/Reddit-Enhancement-Suite',
'hotwired/stimulus',
'htmlunit/htmlunit',
'http4s/http4s',
'huggingface/datasets',
'humhub/humhub',
'hyperium/hyper',
'hyperledger/besu',
'icsharpcode/sharpziplib',
'imagemagick/imagemagick',
'immerjs/immer',
'import-js/eslint-plugin-import',
'infobyte/faraday',
'intel-analytics/BigDL',
'intelowlproject/IntelOwl',
'internetarchive/openlibrary',
'inventree/inventree',
'ipfs/go-ipfs',
'ipfs/kubo',
'ireader/media-server',
'ispc/ispc',
'jaegertracing/jaeger',
'JanDeDobbeleer/oh-my-posh',
'jaredpalmer/formik',
'jazzband/django-debug-toolbar',
'jazzband/django-pipeline',
'jazzband/pip-tools',
'jekyll/jekyll',
'jenkins-x/jx',
'jenkinsci/configuration-as-code-plugin',
'jens-maus/raspberrymatic',
'jeremylong/dependencycheck',
'jessesquires/JSQMessagesViewController',
'jgraph/drawio-desktop',
'jina-ai/jina',
'joncampbell123/dosbox-x',
'josdejong/jsoneditor',
'jrnl-org/jrnl',
'jruby/jruby',
'jsdom/jsdom',
'jsx-eslint/eslint-plugin-react',
'juice-shop/juice-shop',
'junit-team/junit4',
'jupyter-lsp/jupyterlab-lsp',
'jupyter-server/jupyter_server',
'jupyterhub/jupyterhub',
'jupyterlab/jupyterlab-desktop',
'jupyter/jupyter_server',
'jupyter/nbconvert',
'juspay/hyperswitch',
'kareadita/kavita',
'kataras/iris',
'kedacore/keda',
'keeweb/keeweb',
'kevinpapst/kimai2',
'kimai/kimai',
'koajs/koa',
'Kong/insomnia',
'krakenjs/kraken-js',
'kserve/kserve',
'kubeedge/kubeedge',
'kubeovn/kube-ovn',
'kubernetes-client/javascript',
'kubernetes-sigs/aws-load-balancer-controller',
'kubernetes-sigs/cluster-api',
'kubernetes-sigs/controller-runtime',
'kubernetes-sigs/external-dns',
'kubernetes-sigs/kubebuilder',
'kubernetes-sigs/kubespray',
'kubernetes-sigs/kustomize',
'kubernetes/autoscaler',
'kubernetes/dashboard',
'kubernetes/kompose',
'kubernetes/kops',
'kubernetes/test-infra',
'kubesphere/kubesphere',
'kubevela/kubevela',
'kubevirt/containerized-data-importer',
'kubevirt/kubevirt',
'kumahq/kuma',
'kyverno/kyverno',
'laravel/cashier-stripe',
'laravel/valet',
'layer5io/meshery',
'ledgerwatch/erigon',
'liballeg/allegro5',
'libgit2/libgit2',
'libjxl/libjxl',
'liblouis/liblouis',
'libp2p/rust-libp2p',
'librenms/librenms',
'libsndfile/libsndfile',
'libssh2/libssh2',
'libvnc/libvncserver',
'lightdash/lightdash',
'lightningnetwork/lnd',
'linkerd/linkerd2',
'liquibase/liquibase',
]


if __name__ == '__main__':
    # repos(download_attributes)
    prepare_count_dict()
    repos(download_issues)
    # repos(dummy)