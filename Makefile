.PHONY: css watch-tailwind initialize-repo get-tailwind tailwind_config docs

css: tailwind_config
	tailwindcss/tailwindcss -c tailwindcss/tailwind.config.js -i tailwindcss/geant.base.css -o src/geant_argus/geant_argus/static/geant.min.css -m

watch-tailwind: tailwind_config
	tailwindcss/tailwindcss -c tailwindcss/tailwind.config.js -i tailwindcss/geant.base.css -o src/geant_argus/geant_argus/static/geant.css --watch

initialize-repo: cmd.sh config.json src/geant_argus/geant_argus/static/geant.css tailwind_config get-tailwind
	tailwindcss/tailwindcss -c tailwindcss/tailwind.config.js -i tailwindcss/geant.base.css -o src/geant_argus/geant_argus/static/geant.css

tailwind_config: src/geant_argus/geant_argus/static/geant.css
	SECRET_KEY= DJANGO_SETTINGS_MODULE=geant_argus.settings.base django-admin tailwind_config

get-tailwind:
	tailwindcss/get-tailwind.sh

src/geant_argus/geant_argus/static/geant.css:
	touch src/geant_argus/geant_argus/static/geant.css

cmd.sh:
	cp cmd.sh-template cmd.sh && chmod +x cmd.sh

config.json:
	cp config-example.json config.json

docs:
	rm -rf docs/build
	./build-docs.sh