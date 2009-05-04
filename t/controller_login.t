use strict;
use warnings;
use Test::More tests => 3;

BEGIN { use_ok 'Catalyst::Test', 'Savane' }
BEGIN { use_ok 'Savane::Controller::login' }

ok( request('/login')->is_success, 'Request should succeed' );


