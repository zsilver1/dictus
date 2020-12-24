BUILD_DIR = dictus_build
DATA_DIR = data
TEMPLATE_DIR = templates

INPUT_EXT = toml
INPUT_DIR = input

files = $(wildcard $(DATA_DIR)/*) $(wildcard $(TEMPLATE_DIR)/*) $(wildcard $(INPUT_DIR)/*.$(INPUT_EXT))

copy: $(files)
	cp $(DATA_DIR)/* $(BUILD_DIR)/

build: copy
	dictus --in $(INPUT_DIR) --ext $(INPUT_EXT) --out $(BUILD_DIR) --templates $(TEMPLATE_DIR) --data $(DATA_DIR)
