.venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e ".[dev]"
	.venv/bin/python -m playwright install

clean:
	rm -rf .venv

kml: .venv
	.venv/bin/python3 scripts/clean_kml.py --input data/kml/raw/core/TTC_VERIFIED.kml --output data/kml/cleaned/core/TTC_VERIFIED.kml

clean-all-kml: .venv
	.venv/bin/python3 scripts/clean_all_kml.py

screenshot: .venv
	.venv/bin/python3 scripts/screenshot_google_earth.py --kml data/kml/cleaned/extra/block_2_tf_2022.kml --output data/output/extra/block_2_tf_2022.kml

screenshot-all-kml: .venv
	.venv/bin/python3 scripts/screenshot_all_kml.py

train: .venv
	.venv/bin/python3 -m training.train \
		-c configs/sam2.1_training/sam2.1_hiera_b+_single_frame.yaml \
		--use-cluster 0 \
		--num-gpus 1

run-app: .venv
	FLASK_APP=webapp/app.py FLASK_ENV=development .venv/bin/flask run --reload
