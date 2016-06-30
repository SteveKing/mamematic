# MAMEmatic
Browser-based MAME front-end

## API

http://example.com/mamematic/api/v1.0/...

    GET     games               Return all games
    GET     games/[game_id]     Get all details of [game_id]

    GET     lists               Return all game lists
    GET     lists/[list_id]     Return all games on list [list_id]
    POST    lists               Create new game list
    PUT     lists/[list_id]     Update list [list_id]
    DELETE  lists/[list_id]     Delete list [list_id]
