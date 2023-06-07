# geoportal-configuration

Generation of configuration JSONs for Geoportal JS APIs

## Direct usage (for geoportal-access-lib)
Use the file in the `dist` directory of this repo directly in the project. The files are generated each day. Example: https://raw.githubusercontent.com/IGNF/geoportal-configuration/main/dist/essentielsConfig.json

## Dependency install
`pip3 install -r requirements.txt`

## CLI usage
`python main.py key1 key2...`

Config files are generated in `dist` directory

## Launch web interface
### Without Docker
`python -m flask run --host=0.0.0.0`

### With Docker
`docker build --tag gpconnfig . && docker run gpconfig`

## Use web interface
### Form
Go to the index of the deployed web inteface with a web browser. Example: https://geoportal-configuration.onrender.com/

### API
`curl http://host:port/api?key1,key2,...`

Example: https://geoportal-configuration.onrender.com/api?keys=essentiels
