
# update iTunes podcasts

$iTunes = new-Object -comobject iTunes.Application
if($iTunes -ne $null)
{
    'iTunes started' | out-Host

    'Checking for new podcasts' | out-Host
    $iTunes.UpdatePodcastFeeds()
    

    $library = $iTunes.Sources | where { $_.Name -eq 'Library' }
    $podcasts = $library.Playlists | where {$_.Name -eq 'Podcasts'}

    $foundTracks = $True
    $downloadList = New-Object System.Collections.ArrayList
    while($foundTracks)
    {
        Start-Sleep -seconds 10
        $foundTracks = $False
        foreach($track in $podcasts.Tracks | where {!$_.Enabled})
        {
            $foundTracks = $True
            if(($downloadList | where {$_.Name -eq $track.Name}) -eq $null)
            {
                $track.DownloadPodcastEpisode()
                $result = $downloadList.Add($track)
                'Downloading '+$track.Name |out-Host
            }
            else
            {
                'Still downloading '+$track.Name |out-Host
            }
        }
    }

    'Done' | out-Host
}
else
{
    'Error, Unable to find a running iTunes program or start it' | out-Host
}