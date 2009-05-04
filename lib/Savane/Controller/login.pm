package Savane::Controller::login;

use strict;
use warnings;
use parent 'Catalyst::Controller';

=head1 NAME

Savane::Controller::login - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut


=head2 index

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;

#    $c->response->body('Matched Savane::Controller::login in login.');

    $c->stash->{template} = 'templates/login.tt';
}


sub end : Private {
    my ( $self, $c ) = @_;

    return if $c->res->body; # already have a response
    $c->forward( 'Savane::View::TT' ); # render template
}


=head1 AUTHOR

,,,

=head1 LICENSE

This library is free software, you can redistribute it and/or modify
it under the same terms as Perl itself.

=cut

1;
