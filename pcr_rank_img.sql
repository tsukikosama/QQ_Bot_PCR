/*
 Navicat Premium Data Transfer

 Source Server         : t
 Source Server Type    : SQLite
 Source Server Version : 3030001
 Source Schema         : main

 Target Server Type    : SQLite
 Target Server Version : 3030001
 File Encoding         : 65001

 Date: 14/03/2025 13:45:29
*/

PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for pcr_rank_img
-- ----------------------------
DROP TABLE IF EXISTS "pcr_rank_img";
CREATE TABLE "pcr_rank_img" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "title" TEXT NOT NULL,
  "img_url" TEXT NOT NULL,
  "title_id" INTEGER NOT NULL,
  "web_title" TEXT NOT NULL,
  "up_name"
);

-- ----------------------------
-- Auto increment value for pcr_rank_img
-- ----------------------------
UPDATE "sqlite_sequence" SET seq = 2 WHERE name = 'pcr_rank_img';

PRAGMA foreign_keys = true;
