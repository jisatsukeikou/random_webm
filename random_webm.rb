#!/usr/bin/env ruby

require 'tempfile'
require 'json'
require 'open-uri'
require 'optparse'

CHAN_HOST = "https://2ch.hk/"
board = "a"
playlist = false
player_string = "mpv --really-quiet "
player_playlist_options = "--shuffle --playlist="

ATTACH_VIDEO = 6

Webm = Struct.new(:path, :fullname)

def get_vids(board)
  catalog = File.join CHAN_HOST, board, "catalog_num.json"
  catalog_data = JSON.parse(URI.open(catalog).read)

  webm_match = ->(s) { /^[^\.]*WEBM/.match? s }
  webm_filter = ->(attach) { 
    attach["type"] == ATTACH_VIDEO && attach["nsfw"] == 0 
  }

  board_threads = catalog_data['threads'].filter do |thr| 
    webm_match.call(thr['subject']) || webm_match.call(thr['comment'])
  end 
  thread_nums = board_threads.map { |thr| thr['num'] }
  threads = thread_nums.map do |tnum|
    url = File.join CHAN_HOST, board, "res", tnum + ".json"
    tdigest = JSON.parse(URI.open(url).read)
    tdigest["threads"][0]
  end

  attaches = threads
    .map { |thr| thr['posts'] }
    .flatten
    .map { |post| post['files'] }
    .flatten

  webms = attaches.filter(&webm_filter)
  webms = webms.map do |attach| 
    Webm.new(File.join(CHAN_HOST, attach['path']), attach['fullname'])
  end

  webms
end

def make_playlist(vids)
  yield "[playlist]\n"
  vids.map.with_index do |webm, idx|
    # Make a playlist in PLS format with an iterator
    yield "File#{idx}=#{webm.path}\n"
    yield "Title#{idx}=#{webm.fullname}\n"
    yield "\n"
  end
  yield "NumberOfEntries=#{vids.length}\n"
  yield "Version=2\n"
end

OptionParser.new do |p|
  p.on("-b", "--board b") { |b| board = b }
  p.on("-p", "--playlist") { playlist = true }
end.parse!

vids = get_vids(board)

abort "No webms found on /#{board}/" if vids.empty?

destination = String.new

if playlist
  pl_file = Tempfile.new
  player_string += player_playlist_options
  destination = pl_file.path
  make_playlist(vids) { |s| pl_file.write s }
  pl_file.rewind
  puts "Playing all webms on /#{board}/..."
else
  vid = vids.sample
  destination = vid.path
  puts "Playing #{vid.fullname}..."
end

`#{player_string + destination}`
