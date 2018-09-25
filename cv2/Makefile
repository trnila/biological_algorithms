all: ui_main_window.py

ui_%.py: %.ui
	pyuic5 $^ -o $@

clean:
	rm -f ui_*.py

