require "active_support/all"
require 'nokogiri'
require 'open-uri'

module Helpers
  extend ActiveSupport::NumberHelper
end

module Jekyll
  class GoogleScholarCitationsTag < Liquid::Tag
    Citations = { }
    ProfileFetched = { }

    def initialize(tag_name, params, tokens)
      super
      splitted = params.split(" ").map(&:strip)
      @scholar_id = splitted[0]
      @article_id = splitted[1]

      if @scholar_id.nil? || @scholar_id.empty?
        puts "Invalid scholar_id provided"
      end

      if @article_id.nil? || @article_id.empty?
        puts "Invalid article_id provided"
      end
    end

    def render(context)
      article_id = resolve_value(context, @article_id).to_s.strip
      scholar_id = resolve_value(context, @scholar_id).to_s.split(/[&?]/).first.strip
      article_url = "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=#{scholar_id}&citation_for_view=#{scholar_id}:#{article_id}"
      cache_key = "#{scholar_id}:#{article_id}"

      return "N/A" if scholar_id.empty? || article_id.empty? || article_id == scholar_id

      begin
          # If the citation count has already been fetched, return it
          if GoogleScholarCitationsTag::Citations[cache_key]
            return GoogleScholarCitationsTag::Citations[cache_key]
          end

          fetch_profile_citations(scholar_id)
          if GoogleScholarCitationsTag::Citations.key?(cache_key)
            return GoogleScholarCitationsTag::Citations[cache_key]
          end

          # Sleep for a random amount of time to avoid being blocked
          sleep(rand(1.5..3.5))

          # Fetch the article page
          doc = Nokogiri::HTML(URI.open(article_url, "User-Agent" => "Ruby/#{RUBY_VERSION}"))

          # Attempt to extract the "Cited by n" string from the meta tags
          citation_count = nil

          # Look for meta tags with "name" attribute set to "description"
          description_meta = doc.css('meta[name="description"]')
          og_description_meta = doc.css('meta[property="og:description"]')

          if !description_meta.empty?
            cited_by_text = description_meta[0]['content']
            matches = cited_by_text.match(/Cited by\s*(\d[\d,]*)/i)

            if matches
              citation_count = matches[1].sub(",", "").to_i
            end

          elsif !og_description_meta.empty?
            cited_by_text = og_description_meta[0]['content']
            matches = cited_by_text.match(/Cited by\s*(\d[\d,]*)/i)

            if matches
              citation_count = matches[1].sub(",", "").to_i
            end
          end

          if citation_count.nil?
            matches = [doc.text, doc.to_html].filter_map { |text| text.match(/Cited by\s*(\d[\d,]*)/i) }.first
            citation_count = matches[1].delete(",").to_i if matches
          end

        citation_count = if citation_count.nil?
          "N/A"
        else
          Helpers.number_to_human(citation_count, :format => '%n%u', :precision => 2, :units => { :thousand => 'K', :million => 'M', :billion => 'B' })
        end

      rescue Exception => e
        # Handle any errors that may occur during fetching
        citation_count = "N/A"

        # Print the error message including the exception class and message
        puts "Error fetching citation count for #{article_id} in #{article_url}: #{e.class} - #{e.message}"
      end

      GoogleScholarCitationsTag::Citations[cache_key] = citation_count
      return "#{citation_count}"
    end

    private

    def resolve_value(context, markup)
      Liquid::Variable.new(markup.strip).render(context)
    rescue Exception
      context[markup.strip]
    end

    def fetch_profile_citations(scholar_id)
      return if GoogleScholarCitationsTag::ProfileFetched[scholar_id]

      profile_url = "https://scholar.google.com/citations?user=#{scholar_id}&hl=en&pagesize=100"
      profile_html = URI.open(profile_url, "User-Agent" => "Ruby/#{RUBY_VERSION}").read
      profile_html.scan(/<tr class="gsc_a_tr">(.*?)(?=<tr class="gsc_a_tr">|<\/tbody>)/m) do |row_match|
        row = row_match[0]
        article_id = row[/citation_for_view=#{Regexp.escape(scholar_id)}:([^&"]+)/, 1]
        next if article_id.nil? || article_id.empty?

        count_text = row[/class="gsc_a_ac gs_ibl">([^<]*)<\/a>/m, 1].to_s
        count = count_text.gsub(/[^\d]/, "")
        GoogleScholarCitationsTag::Citations["#{scholar_id}:#{article_id}"] = count.empty? ? "0" : Helpers.number_to_human(count.to_i, :format => '%n%u', :precision => 2, :units => { :thousand => 'K', :million => 'M', :billion => 'B' })
      end

      GoogleScholarCitationsTag::ProfileFetched[scholar_id] = true
    rescue Exception => e
      puts "Error fetching Google Scholar profile for #{scholar_id}: #{e.class} - #{e.message}"
      GoogleScholarCitationsTag::ProfileFetched[scholar_id] = true
    end
  end
end

Liquid::Template.register_tag('google_scholar_citations', Jekyll::GoogleScholarCitationsTag)
