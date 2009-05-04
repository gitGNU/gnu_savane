package Savane::Controller::Root;

use strict;
use warnings;
use parent 'Catalyst::Controller';

#
# Sets the actions in this controller to be registered with no prefix
# so they function identically to actions created in MyApp.pm
#
__PACKAGE__->config->{namespace} = '';

=head1 NAME

Savane::Controller::Root - Root Controller for Savane

=head1 DESCRIPTION

[enter your description here]

=head1 METHODS

=cut

=head2 index

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;

    # example of a template being called
    $c->stash->{remote_host} = $c->req->address;
    $c->stash->{template} = 'templates/main_page.tt';
}

sub default :Path {
    my ( $self, $c ) = @_;
    $c->response->body( 'Page not found' );
    $c->response->status(404);

}

=head2 end

Allow for "post processing" of in our application.
* Write some code for handling "server errors".
* Also, attempt to render a view, if needed.

=cut

sub end : Private {
    my ( $self, $c ) = @_;

    return if $c->res->body; # already have a response
    $c->forward( 'Savane::View::TT' ); # render template
}

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
