package Savane::Model::DB;

use strict;
use base 'Catalyst::Model::DBIC::Schema';

# Gather DBI configuration from config

if (my $db_conf = Savane->config->{database})
{
    die "fatal error: 'database' not configured in database configuration\n"
        unless $db_conf->{database};

    die "fatal error: 'user' not configured in database configuration\n"
        unless $db_conf->{user};

    my $dbi_string = "dbi:mysql:dbname=$db_conf->{database}";
    $dbi_string .= ";host=$db_conf->{host}" if $db_conf->{host};
    $dbi_string .= ";host=$db_conf->{port}" if $db_conf->{port};
    
    my @user_auth = ( $db_conf->{user} );
    push @user_auth, $db_conf->{password} if $db_conf->{password};

    __PACKAGE__->config(
        schema_class => 'Savane::Schema',
        connect_info => [
            $dbi_string,
            @user_auth
        ],   
    );
}
else
{
    die "fatal error: database settings not configured in ./savane.conf\n";
}


=head1 NAME

Savane::Model::DB - Catalyst DBIC Schema Model

=head1 SYNOPSIS

See L<Savane>

=head1 DESCRIPTION

L<Catalyst::Model::DBIC::Schema> Model using schema L<Savane::Schema>

=head1 AUTHOR

Michael J. Flickinger  C<< <mjflick@gnu.org> >>

=head1 LICENSE

    Savane
    Copyright (C) 2009 - Savannah Hackers

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

=cut

1;
