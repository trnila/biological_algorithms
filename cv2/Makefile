all: ui_main_window.py resources_rc.py

ui_%.py: %.ui
	pyuic5 $^ -o $@

resources_rc.py: resources.qrc
	pyrcc5 -o $@ $^

clean:
	rm -f ui_*.py

