BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
  profile_name   => 'GSIS_OCIGENAI_COHERE',
  attributes     =>'{"provider": "oci",
            "model": "cohere.command-r-plus-08-2024",
            "region": "eu-frankfurt-1",
            "conversation": "true",
			"credential_name": "OCI$RESOURCE_PRINCIPAL",
			"object_list": [{"owner": "USAGE", "name": "OCI_COST_USAGE_MONTHLY_V"}]
       }');
END;

BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
  profile_name   => 'GSIS_OCIGENAI',
  attributes     =>'{"provider": "oci",
            "model": "meta.llama-3.3-70b-instruct",
            "region": "eu-frankfurt-1",
			"credential_name": "OCI$RESOURCE_PRINCIPAL",
			"object_list": [{"owner": "USAGE", "name": "OCI_COST_USAGE_MONTHLY_V"}]
       }');
END;