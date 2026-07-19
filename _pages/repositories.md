---
layout: page
permalink: /repositories/
title: repositories
description:
nav: true
nav_order: 4
---

{% if site.data.repositories.github_users %}

## GitHub users

<div class="repositories github-users d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for user in site.data.repositories.github_users %}
    {% include repository/repo_user.liquid username=user %}
  {% endfor %}
</div>

{% endif %}

{% if site.data.repositories.github_repos %}

## GitHub Repositories

<div class="repositories repo-grid d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for repo in site.data.repositories.github_repos %}
    {% include repository/repo.liquid repository=repo %}
  {% endfor %}
</div>
{% endif %}

<style>
  .github-users {
    align-items: stretch !important;
  }

  .github-users .repo-user {
    flex: 0 0 50%;
    max-width: 50%;
  }

  .repo-user-card {
    display: flex;
    gap: 1rem;
    height: 100%;
    min-height: 8rem;
    padding: 1rem;
    color: var(--global-text-color);
    text-align: left;
    text-decoration: none;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 6px;
  }

  .repo-user-card:hover {
    color: var(--global-text-color);
    text-decoration: none;
    border-color: var(--global-theme-color);
    box-shadow: 0 4px 14px rgb(0 0 0 / 10%);
  }

  .repo-user-avatar {
    width: 4.5rem;
    height: 4.5rem;
    flex: 0 0 4.5rem;
    border-radius: 50%;
  }

  .repo-user-body {
    min-width: 0;
  }

  .repo-user-name {
    color: var(--global-theme-color);
    font-size: 1.1rem;
    font-weight: 700;
  }

  .repo-user-username {
    margin-bottom: 0.35rem;
    color: var(--global-text-color-light);
    font-size: 0.9rem;
  }

  .repo-user-bio {
    margin-bottom: 0.5rem;
    color: var(--global-text-color);
    font-size: 0.95rem;
    line-height: 1.4;
  }

  .repo-user-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    color: var(--global-text-color-light);
    font-size: 0.85rem;
  }

  .repo-grid {
    align-items: stretch !important;
    gap: 1rem;
  }

  .repo-grid .repo {
    flex: 0 0 calc((100% - 2rem) / 3);
    max-width: calc((100% - 2rem) / 3);
  }

  .repo-grid .repo-card {
    height: 30rem;
    min-height: 16rem;
    overflow: hidden;
  }

  .repo-card {
    display: flex;
    flex-direction: column;
    color: var(--global-text-color);
    text-decoration: none;
    background: var(--global-card-bg-color);
    border: 1px solid var(--global-divider-color);
    border-radius: 6px;
    transition:
      border-color 0.15s ease,
      transform 0.15s ease,
      box-shadow 0.15s ease;
  }

  .repo-cover {
    width: 100%;
    aspect-ratio: 1200 / 630;
    object-fit: cover;
    border-bottom: 1px solid var(--global-divider-color);
    border-radius: 6px 6px 0 0;
  }

  .repo-readme-image {
    width: calc(100% - 2rem);
    height: 9rem;
    object-fit: contain;
    margin: 1rem 1rem 0;
    background: #fff;
    border: 1px solid var(--global-divider-color);
    border-radius: 4px;
  }

  .repo-card:hover {
    color: var(--global-text-color);
    text-decoration: none;
    border-color: var(--global-theme-color);
    box-shadow: 0 4px 14px rgb(0 0 0 / 10%);
    transform: translateY(-1px);
  }

  .repo-card-title {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin: 1rem 1rem 0.6rem;
    color: var(--global-theme-color);
    font-size: 1.05rem;
    font-weight: 700;
  }

  .repo-card-description {
    display: -webkit-box;
    min-height: 4.15rem;
    margin: 0 1rem 1rem;
    overflow: hidden;
    color: var(--global-text-color);
    font-size: 0.95rem;
    line-height: 1.45;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
  }

  .repo-card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: auto;
    margin: 0 1rem 1rem;
    color: var(--global-text-color-light);
    font-size: 0.85rem;
  }

  .repo-language {
    display: inline-flex;
    gap: 0.35rem;
    align-items: center;
  }

  .repo-language-dot {
    width: 0.75rem;
    height: 0.75rem;
    border-radius: 50%;
  }

  @media (max-width: 992px) {
    .repo-grid .repo {
      flex-basis: calc((100% - 1rem) / 2);
      max-width: calc((100% - 1rem) / 2);
    }
  }

  @media (max-width: 576px) {
    .github-users .repo-user {
      width: 100%;
      max-width: 100%;
      flex-basis: 100%;
    }

    .repo-user-card {
      flex-direction: column;
    }

    .repo-grid .repo {
      width: 100%;
      max-width: 100%;
      flex-basis: 100%;
    }
  }
</style>
