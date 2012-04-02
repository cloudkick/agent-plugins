#!/usr/bin/env ruby

# Author: James Turnbull
# Copyright (c) 2012 James Turnbull <james@lovedthanlost.net>
#
# MIT License:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


hostname = `hostname -s`.chomp

begin
  status = `cman_tool nodes -n #{hostname} -F type`
  case status
  when 'X'
    puts "status err Cluster node #{hostname} is not a member of the cluster."
  when 'd'
    puts "status err Cluster node #{hostname} is disallowed from the cluster."
  else
   puts "status ok Cluster node #{hostname} is a member of the cluster." 
  end
rescue => e
  puts "status err Problem running cman_tool plugin: #{e.message}"
end
