package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

// endpoints to use
var dotaapi = "https://api.opendota.com/api"

// Create a User struct to represent calls made to the OpenDota API
type User struct {
	ID string
}

type Hero struct {
	ID   uint   `json:"id"`
	Name string `json:"localized_name"`
}

type MatchInfo struct {
	MatchID  uint64 `json:"match_id"`
	GameMode uint   `json:"game_mode"`
}

type GameInfo struct {
	Players []struct {
		AccountID uint64 `json:"account_id"`
		Nickname  string `json:"personaname"`
		Kills     uint64 `json:"kills"`
		Deaths    uint64 `json:"deaths"`
		Assists   uint64 `json:"assists"`
	}
}

func LoadHeroes() []Hero {
	dat, err := ioutil.ReadFile("heroes.json")
	if err != nil {
		// File is most likely not found
		r := fetch(fmt.Sprintf("%s/heroes", dotaapi), "Failed to fetch Hero Data")
		we := ioutil.WriteFile("heroes.json", r, 0655)
		if we != nil {
			panic("Failed to write to file")
		}

		var v []Hero
		e := json.Unmarshal(r, &v)
		if e != nil {
			panic("Couldn't parse Hero JSON data")
		}
		return v
	}
	var v []Hero
	e := json.Unmarshal(dat, &v)
	if e != nil {
		panic("Hero file corrupted and can't be read")
	}
	return v
}

func fetch(url string, errmsg string) []byte {
	resp, err := http.Get(url)
	if err != nil {
		panic(errmsg)
	}
	data, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic("Failed to read data blob")
	}
	return data
}

func LastMatch(uid uint64) uint64 {
	s := fmt.Sprintf("%s/players/%d/matches?limit=1", dotaapi, uid)
	r := fetch(s, "Failed to get Matches")

	var j []MatchInfo
	err := json.Unmarshal(r, &j)
	if err != nil {
		panic("Failed to read JSON")
	}

	for _, match := range j {
		return match.MatchID
	}
	return 0
}

func ParseMatch(mid uint64, uid uint64) {
	heroes := LoadHeroes()
	for _, x := range heroes {
		fmt.Println(x)
	}

	s := fmt.Sprintf("%s/matches/%d", dotaapi, mid)
	r := fetch(s, "Failed to get game data")

	var j GameInfo
	err := json.Unmarshal(r, &j)
	if err != nil {
		panic("Failed to read JSON")
	}

	// start parsing the game info here
	for _, player := range j.Players {
		if player.AccountID == uid {
			fmt.Println("Found the player")
		}
	}

	fmt.Println(j)
}

func main() {
	var steve uint64
	steve = 40281889
	last := LastMatch(steve)
	fmt.Println("Steve's last match was", last)
	ParseMatch(last, steve)
	return
}
