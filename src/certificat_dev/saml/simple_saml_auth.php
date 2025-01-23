<?php

$test_user_base = array(
    // put base attributes here    
);

$config = array(
    'admin' => array(
        'core:AdminPassword',
    ),
    'example-userpass' => array(
        'exampleauth:UserPass',
        'user:password' => array_merge($test_user_base, array(
            'uid' => 'genusr',
            'mail' => 'genusr@idp.local',
            'givenName' => 'Generic',
            'sn' => 'User',
            'memberof' => array('first-group', 'second-group', 'third-group')
        )),
        'admin:password' => array_merge($test_user_base, array(
            'uid' => 'admusr',
            'mail' => 'admusr@idp.local',
            'givenName' => 'Admin',
            'sn' => 'User',
            'memberof' => array('admin-group', 'first-group', 'second-group')
        )),
        'invalid:invalid' => array_merge($test_user_base, array(
            'email' => 'admusr@idp.local',
            'givenName' => 'Admin',
            'sn' => 'User',
            'memberof' => array('admin-group', 'first-group', 'second-group')
        )),
        'eptid:eptid' => array_merge($test_user_base, array(
            'eduPersonTargetedID' => '123456'
        )),
        'external:external' => array_merge($test_user_base, array(
            'mail' => 'socialuser@idp.local',
            'givenName' => 'Admin',
            'sn' => 'User',
        )),
        'eppn:eppn' => array_merge($test_user_base, array(
            'eduPersonPrincipalName' => 'eppn@acme.edu'
        ))
    ),
);
