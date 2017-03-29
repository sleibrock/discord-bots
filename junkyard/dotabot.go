package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

// endpoints to use
var web_link = "https://discordapp.com/api/webhooks/296303788057427969/CUr6cezgCmIjYfVrbcxTIu2HnFKSorOUv15DKwnOoEvJcTFx8ZMNRR5RhQyNCqodHCHI"
var dota_api = "https://api.opendota.com/api"
var matchurl = "https://opendota.com/matches"

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

type Rune struct {
	Bounty uint `json:"5"`
}

type Player struct {
	AccountID uint64 `json:"account_id"`
	Nickname  string `json:"personaname"`
	HeroID    uint   `json:"hero_id"`
	Kills     uint64 `json:"kills"`
	Deaths    uint64 `json:"deaths"`
	Assists   uint64 `json:"assists"`
	IsRadiant bool   `json:"isRadiant"`
	Pings     uint   `json:"pings"`
	GPM       uint   `json:"gold_per_min"`
	XPM       uint   `json:"xp_per_min"`
	Runes     Rune   `json:"runes"`
}

type GameInfo struct {
	MatchID      uint64   `json:"match_id"`
	RadiantScore uint     `json:"radiant_score"`
	DireScore    uint     `json:"dire_score"`
	GameMode     uint     `json:"game_mode"`
	RadiantWin   bool     `json:"radiant_win"`
	Players      []Player `json:"players"`
	Chat         []struct {
		PlayerNick string `json:"unit"`
		Message    string `json:"key"`
	}
}

type Embed struct {
	Title       string   `json:"title"`
	Description string   `json:"description"`
	URL         string   `json:"url"`
	Color       uint     `json:"color"`
	Fields      []EField `json:"fields"`
}

type EField struct {
	Name   string `json:"name"`
	Value  string `json:"value"`
	Inline bool   `json:"inline"`
}

type Message struct {
	Embeds []Embed `json:"embeds"`
}

func (g GameInfo) GetData(uid uint64, heroes []Hero) Message {
	var fields []EField

	var p Player
	for _, player := range g.Players {
		if player.AccountID == uid {
			p = player
		}
	}
	if p == (Player{}) {
		panic("Failed to find user ID")
	}

	var hero Hero
	for _, h := range heroes {
		if h.ID == p.HeroID {
			hero = h
		}
	}

	var victory string
	if g.RadiantWin && p.IsRadiant {
		victory = "won"
	} else {
		victory = "lost"
	}

	// Very basic field
	fields = append(fields, EField{
		"K/D/A",
		fmt.Sprintf("%d/%d/%d", p.Kills, p.Deaths, p.Assists),
		true,
	})

	fields = append(fields, EField{
		"GPM / GPM",
		fmt.Sprintf("%d / %d", p.GPM, p.XPM),
		true,
	})

	// Bounty rune field
	if p.Runes != (Rune{}) {
		fields = append(fields, EField{
			"Bounty Runes Collected",
			fmt.Sprintf("%d", p.Runes.Bounty),
			true,
		})
	}

	// Calculate the Ping statistic
	if p.Pings != 0 {
		fields = append(fields, EField{
			"Pings Used",
			fmt.Sprintf("%d", p.Pings),
			true,
		})
	}

	// search for longest chat message
	var longest string
	for _, chat := range g.Chat {
		if chat.PlayerNick == p.Nickname {
			if len(chat.Message) > len(longest) {
				longest = chat.Message
			}
		}
	}
	if longest != "" {
		fields = append(fields, EField{
			"Longest Chat",
			fmt.Sprintf("'%s' -%s", longest, p.Nickname),
			true,
		})
	}

	msg := Message{
		[]Embed{
			Embed{
				fmt.Sprintf("Results for Match %d", g.MatchID),
				fmt.Sprintf(p.Nickname + " " + victory + " as " + hero.Name),
				fmt.Sprintf("%s/%d", matchurl, g.MatchID),
				200, // color
				fields,
			},
		},
	}
	return msg
}

func LoadHeroes() []Hero {
	dat, err := ioutil.ReadFile("heroes.json")
	if err != nil {
		// File is most likely not found
		r := fetch(fmt.Sprintf("%s/heroes", dota_api), "Failed to fetch Hero Data")
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

func post(msg Message) {
	jv, err := json.Marshal(msg)
	if err != nil {
		panic("Can't construct JSON message")
	}
	_, err2 := http.Post(web_link, "application/json", bytes.NewBuffer(jv))
	if err2 != nil {
		panic("Failed to send WebHook message")
	}
}

func LastMatch(uid uint64) uint64 {
	s := fmt.Sprintf("%s/players/%d/matches?limit=1", dota_api, uid)
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

func ParseMatch(mid uint64, uid uint64, heroes []Hero) {
	s := fmt.Sprintf("%s/matches/%d", dota_api, mid)
	r := fetch(s, "Failed to get game data")

	var game GameInfo
	err := json.Unmarshal(r, &game)
	if err != nil {
		panic("Failed to read JSON")
	}

	// start parsing the game info here
	msg := game.GetData(uid, heroes)
	post(msg)
}

func main() {
	var steve uint64
	steve = 40281889
	heroes := LoadHeroes()
	last := LastMatch(steve)
	fmt.Println("Steve's last match was", last)
	fmt.Println("Printing match to Discord")
	ParseMatch(last, steve, heroes)
	fmt.Println("Done")
	return
}

// end
