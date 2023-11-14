venv: venv_projet_nhl/bin/activate
	source venv_projet_nhl/bin/activate

see_config_train:
	python3 Milestone2/training_main.py --cfg job > /tmp/toto.yaml && yq /tmp/toto.yaml

see_config_hp_opt:
	python3 Milestone2/hp_opt_main.py --cfg job > /tmp/toto.yaml && yq /tmp/toto.yaml

clean:
	rm -rf log_file outputs training_artifacts

run_baseline:
	python3 Milestone2/training_main.py --multirun model=logistic_regression,xgboost

del_bp:
	for i in $(ag 'import pdb; pdb.set_trace()' -l); do sed --debug -i '/import pdb; pdb.set_trace()/d' $i; done