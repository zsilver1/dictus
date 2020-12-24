BUILD_DIR = dictus_build
DATA_DIR = data
TEMPLATE_DIR = templates

INPUT_DIALECT = yaml
INPUT_DIR = input

files = $(wildcard $(DATA_DIR)/*) $(wildcard $(TEMPLATE_DIR)/*) $(wildcard $(INPUT_DIR)/*.$(INPUT_DIALECT))

copy: $(files)
	cp $(DATA_DIR)/* $(BUILD_DIR)/

build: copy
	dictus --in $(INPUT_DIR) --dialect $(INPUT_DIALECT) --out $(BUILD_DIR) --templates $(TEMPLATE_DIR) --data $(DATA_DIR)
