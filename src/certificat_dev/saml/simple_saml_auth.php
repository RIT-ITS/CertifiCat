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
        ))
    ),
);
