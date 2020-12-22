BUILD_DIR = dictus_build
DATA_DIR = data
TEMPLATE_DIR = templates

INPUT_EXT = md
INPUT_DIR = markdown

files = $(DATA_DIR)/* $(TEMPLATE_DIR)/* $(INPUT_DIR)/*.$(INPUT_EXT)

copy:
	cp $(DATA_DIR)/* $(BUILD_DIR)/

build: copy $(files)
	dictus --in $(INPUT_DIR) --ext $(INPUT_EXT) --out $(BUILD_DIR) --templates $(TEMPLATE_DIR) --data $(DATA_DIR)
