package Savane;

use strict;
use warnings;

use Catalyst::Runtime '5.70';

# Set flags and add plugins for the application
#
#         -Debug: activates the debug mode for very useful log messages
#   ConfigLoader: will load the configuration from a Config::General file in the
#                 application's home directory
# Static::Simple: will serve static files from the application's root 
#                 directory

use parent qw/Catalyst/;

our $VERSION = '0.01';

# Configure the application. 
#
# Note that settings in savane.conf (or other external
# configuration file that you set up manually) take precedence
# over this when using ConfigLoader. Thus configuration
# details given here can function as a default configuration,
# with a external configuration file acting as an override for
# local deployment.

__PACKAGE__->config( name => 'Savane' );

# Start the application
__PACKAGE__->setup(qw/-Debug ConfigLoader Static::Simple/);

=head1 NAME

Savane - Web framework for Savane interface.

=head1 SYNOPSIS

    script/savane_server.pl

=head1 DESCRIPTION

Savane

=head1 SEE ALSO

L<Savane::Controller::Root>, L<Catalyst>

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
