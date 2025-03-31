.PHONY: css watch-tailwind initialize-repo

css:
	SECRET_KEY= DJANGO_SETTINGS_MODULE=geant_argus.settings.base django-admin tailwind_config
	tailwindcss -c tailwindcss/tailwind.config.js -i tailwindcss/geant.base.css -o src/geant_argus/geant_argus/static/geant.min.css -m

watch-tailwind:
	SECRET_KEY= DJANGO_SETTINGS_MODULE=geant_argus.settings.base django-admin tailwind_config
	tailwindcss -c tailwindcss/tailwind.config.js -i tailwindcss/geant.base.css -o src/geant_argus/geant_argus/static/geant.css --watch

initialize-repo: cmd.sh
	touch src/geant_argus/geant_argus/static/geant.css
	SECRET_KEY= DJANGO_SETTINGS_MODULE=geant_argus.settings.base django-admin tailwind_config
	tailwindcss -c tailwindcss/tailwind.config.js -i tailwindcss/geant.base.css -o src/geant_argus/geant_argus/static/geant.css

cmd.sh:
	cp cmd.sh-template cmd.sh && chmod +x cmd.sh