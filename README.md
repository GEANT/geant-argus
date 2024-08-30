# Geant Argus

Geant specific customizations for [Argus](https://github.com/Uninett/Argus/) and
[argus-htmx-frontend](https://github.com/Uninett/argus-htmx-frontend/) for use of Argus in the
Geant NOC

Argus is an existing incident aggregator and -dashboard application developed by
Sikt/Uninett/Norgenet. As of 2024, it is envisioned to replace the current Geant dashboard alarms
frontend for the NOC. Argus is an application written in Django. This web framework has excellent
extension/customization capabilities, which makes it relatively easy to slightly modify
applications written in Django

## Development

### Installation

Install this package editable

```python
pip install -e .[dev]
```

alternatively you can also install [Argus](https://github.com/Uninett/Argus/) and
[argus-htmx-frontend](https://github.com/Uninett/argus-htmx-frontend/) editable by first checking
out those repos

### Database
Get a postgres database. For example, you can start one using docker:

```
docker run -e POSTGRES_USER=argus -e POSTGRES_DB=argus -e POSTGRES_PASSWORD=some_password -p 5432:5432 postgres
```

### Create a cmd.sh

To help with setting the correct environment variables, you can create a `cmd.sh` from the
`cmd.sh-template`.

```bash
cp cmd.sh-template cmd.sh
chmod +x cmd.sh
```

Then fill in the required environment variables such as `SECRET_KEY` and `DATABASE_URL`.
For development, `SECRET_KEY` can be any random string. For production usage, a secret key should
be created using `./cmd.sh gen_secret_key`. `DATABASE_URL` should point to the database you set up
in the previous step

You can then call Django management commands through this cmd (eg. `./cmd.sh runserver`)

### Tailwind

This project uses Tailwind together with Daisy UI for css styling. It is recommended to use the
[standalone CLI](https://tailwindcss.com/blog/standalone-cli). In that case make sure to use a
version that [includes DaisyUI](https://github.com/dobicinaitis/tailwind-cli-extra/releases).
Download the correct version for you platform. For example, for linux you could do:

```bash
VERSION=1.7.12
curl -sLo tailwindcss https://github.com/dobicinaitis/tailwind-cli-extra/releases/download/v${VERSION}/tailwindcss-extra-linux-arm64
chmod +x tailwindcss

# Optionally: move the executable somehwere on your PATH (eg. ~/bin or /usr/local/bin)
mv tailwindcss ~/bin
```

_Note_ the above commands can also be used to upgrade `tailwind-cli-extra` when a newer version of
Tailwind or DaisyUI has been released. Adjust the `VERSION` variable appropriately

You then need to generate a `tailwind.config.js` that points to the installed dependencies and
build the tailwind css:

```bash
./cmd.sh tailwind_config
tailwindcss -c tailwindcss/tailwind.config.js -i tailwindcss/geant.base.css -o src/geant_argus/geant_argus/static/geant.css
```

Alternatively, you can use the following command to launch `tailwindcss` in watch mode so that
changes are picked up automatically:

```bash
make watch-tailwind
```

#### Updating the CSS file on commit
During development you should create your css file as `geant.css` using the above steps. However,
for packaging and production. We use a minified version of the css file. This file is included in
the repository and package. If you're committing any changes to `tailwind.config.template.js` or
any of the templates, you should also update the minified version of
`src/geant_argus/geant_argus/static/geant.min.css` by running

```bash
make css
```
### Prepare database for first use
If you are connected to a virgin postgres database, you first need to prepare it

```
./cmd.sh migrate
./cmd.sh initial_setup
```

you can add a fake incident using the following management command

```
./cmd.sh create_fake_incident --metadata-file metadata.sample.json
```

### Run the server

You can now run the development server

```
./cmd.sh runserver
```

