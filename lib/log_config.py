#   Copyright 2013 Mugsy Mcgeee
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys
import logging


logging.getLogger('augr').addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('augr').setLevel(logging.DEBUG)

logging.getLogger('spout').addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('spout').setLevel(logging.INFO)

logging.getLogger('parsing').addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('parsing').setLevel(logging.DEBUG)

logging.getLogger('squeeze').addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('squeeze').setLevel(logging.DEBUG)

logging.getLogger('ui.gui').addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('ui.gui').setLevel(logging.DEBUG)

logging.getLogger('configulifier').addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('configulifier').setLevel(logging.DEBUG)

logging.getLogger('plotandscheme').addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('plotandscheme').setLevel(logging.DEBUG)

logging.getLogger('util').addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('util').setLevel(logging.DEBUG)
