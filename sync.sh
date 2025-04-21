#!/bin/bash

cd ~/seven_emb/seven_emb
git pull origin
cd ~/seven_emb/test
\cp ~/seven_emb/seven_emb/*.py ~/seven_emb/test/
\cp ~/seven_emb/seven_emb/base/*.py ~/seven_emb/test/base/
\cp ~/seven_emb/seven_emb/model/*.py ~/seven_emb/test/model/
\cp ~/seven_emb/seven_emb/common/*.py ~/seven_emb/test/common/
\cp ~/seven_emb/seven_emb/config/*.py ~/seven_emb/test/config/
