#!/usr/bin/perl

# get directory
( $dir ) = `pwd`; chomp $dir;

print "Dir: $dir\n";

if ($dir =~ /(\w+)\/(\w+)\/(\w+)$/) {
	$type = $2;
	$name = $3;
	print "\tTWO: $type\n";
	print "\tTHREE: $name\n";
}

@files = `ls -1 *.mp4 *.m4v`;
chomp @files;

$length = @files;

my $count = 0;
foreach $foo (@files) {
    $count++;
    print "Processing $foo: $count / $length\n";

    # mobile_suit_gundam-the_origin-s01e01
    ( $temp ) = split /\./, $foo;
    my @temp_split = split /-/, $temp;
    
    if (scalar @temp_split > 2) {
        $name = join "-", @temp_split[0..scalar(@temp_split)-2];
    } else {
        ( $name, $temp ) = @temp_split;
    }

    $name =~ s/_/ /g;

    if ( $temp_split[-1] =~ /s(\d+)e(\d+)/) {
        $season = $1;
        $episode = $2;
    }

    $name = upper_first( $name );
    $name =~ s/ The/ the/g; # preserve lowercase "the" in series title
    $title = sprintf("%s s%02de%02d", $name, $season, $episode );
    $cmd = sprintf("AtomicParsley $foo --title '$title' --TVShowName '$name' --TVSeasonNum $season --TVEpisodeNum $episode --overWrite --encodingTool ''\n");
    print "$cmd\n";
    system( $cmd );
}

sub upper_first( $ ) {
	my $tmp = shift @_;
	my @tt = ();
	my @ret = ();

	$tt = $tmp;
	$tt =~ s/^/ /; 
	$tt =~ s/\s(\w+)/ \u$1/g; 
	$tt =~ s/^ //;
	push @ret, $tt;

	return join ' ', @ret;
}
