token=null
compteur=0
while [ "$token" == "null" ] && [[ $compteur != 10 ]]
do
	sleep 5
 	compteur=$((compteur+1))

	user=`curl --request POST \
	  	  --url https://sso.geopf.fr/realms/geoplateforme/protocol/openid-connect/token \
		  --header "content-type: application/x-www-form-urlencoded" \
		  -d 'client_id='$1'&client_secret='$2'&grant_type=client_credentials'`

	token=`echo $user | jq '.access_token' | cut -d'"' -f2`
done

fichier="dist/fullConfig.json"

resultat=`curl --request GET \
  --url "https://data.geopf.fr/api/datastores/2d4dd9f5-ce16-4e7f-81d5-7e392209b7ff/annexes?limit=1&path=/$dossier/$fichier" \
  --header "Authorization: Bearer $token"`

id_annexe=`echo $resultat | jq '.[0]._id' | cut -d'"' -f2`
echo $id_annexe

curl --request PUT \
  --url https://data.geopf.fr/api/datastores/2d4dd9f5-ce16-4e7f-81d5-7e392209b7ff/annexes/$id_annexe \
  --header "Authorization: Bearer $token" \
  --header 'Content-Type: multipart/form-data' \
  --form file=@$fichier

