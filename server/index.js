/**
 * 跳海社区 Skill — MCP Server (Streamable HTTP)
 *
 * 部署目标：腾讯 CloudBase 云函数
 * 协议：MCP Streamable HTTP
 *
 * 工具列表（15个）：
 *   查询类（13个）：get_store_info, get_menu_info, get_service_info, get_events,
 *     get_bartender_info, get_community_info, get_collab_info, get_social_good,
 *     get_brand_story, get_founder_story, get_media_coverage, get_business_model, get_join_us
 *   漂流瓶（2个）：post_bottle, get_bottles
 */

const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

// ============================================================
// Data loading utilities
// ============================================================

// CloudBase: data/ is in same directory; local dev: data/ is in parent
const DATA_DIR = fs.existsSync(path.join(__dirname, "data"))
  ? path.join(__dirname, "data")
  : path.join(__dirname, "..", "data");

function loadYaml(relativePath) {
  const fullPath = path.join(DATA_DIR, relativePath);
  if (!fs.existsSync(fullPath)) return null;
  return yaml.load(fs.readFileSync(fullPath, "utf8"));
}

function loadYamlDir(dirName) {
  const dirPath = path.join(DATA_DIR, dirName);
  if (!fs.existsSync(dirPath)) return [];
  const results = [];
  for (const file of fs.readdirSync(dirPath)) {
    if (file.endsWith(".yaml") && !file.startsWith("_")) {
      results.push({ file, data: loadYaml(path.join(dirName, file)) });
    }
  }
  return results;
}

// ============================================================
// Feishu Bitable client (for bottles & future realtime data)
// ============================================================

const FEISHU_CONFIG = {
  appId: process.env.FEISHU_APP_ID || null,
  appSecret: process.env.FEISHU_APP_SECRET || null,
  bottleTableAppToken: process.env.FEISHU_BOTTLE_APP_TOKEN || null,
  bottleTableId: process.env.FEISHU_BOTTLE_TABLE_ID || null,
  menuTableAppToken: process.env.FEISHU_MENU_APP_TOKEN || null,
  menuTableId: process.env.FEISHU_MENU_TABLE_ID || null,
  eventTableAppToken: process.env.FEISHU_EVENT_APP_TOKEN || null,
  eventTableId: process.env.FEISHU_EVENT_TABLE_ID || null,
};

let feishuTokenCache = { token: null, expiresAt: 0 };

async function getFeishuToken() {
  if (!FEISHU_CONFIG.appId || !FEISHU_CONFIG.appSecret) return null;
  if (feishuTokenCache.token && Date.now() < feishuTokenCache.expiresAt) {
    return feishuTokenCache.token;
  }
  try {
    const resp = await fetch(
      "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          app_id: FEISHU_CONFIG.appId,
          app_secret: FEISHU_CONFIG.appSecret,
        }),
      }
    );
    const data = await resp.json();
    if (data.tenant_access_token) {
      feishuTokenCache = {
        token: data.tenant_access_token,
        expiresAt: Date.now() + (data.expire - 300) * 1000,
      };
      return data.tenant_access_token;
    }
  } catch (e) {
    console.error("Failed to get Feishu token:", e.message);
  }
  return null;
}

async function feishuBitableQuery(appToken, tableId, filter) {
  const token = await getFeishuToken();
  if (!token) return null;
  try {
    const url = `https://open.feishu.cn/open-apis/bitable/v1/apps/${appToken}/tables/${tableId}/records/search`;
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ filter, page_size: 100 }),
    });
    const data = await resp.json();
    return data.data?.items || [];
  } catch (e) {
    console.error("Feishu query error:", e.message);
    return null;
  }
}

async function feishuBitableInsert(appToken, tableId, fields) {
  const token = await getFeishuToken();
  if (!token) return null;
  try {
    const url = `https://open.feishu.cn/open-apis/bitable/v1/apps/${appToken}/tables/${tableId}/records`;
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ fields }),
    });
    return await resp.json();
  } catch (e) {
    console.error("Feishu insert error:", e.message);
    return null;
  }
}

// ============================================================
// Tool implementations
// ============================================================

function toolGetStoreInfo(params) {
  const files = loadYamlDir("stores");
  let allStores = [];
  for (const { file, data } of files) {
    if (!data?.stores) continue;
    for (const store of data.stores) {
      if (params.city && !store.city?.includes(params.city)) continue;
      if (
        params.store_name &&
        !store.name?.includes(params.store_name) &&
        !store.id?.includes(params.store_name)
      )
        continue;
      allStores.push(store);
    }
  }
  if (!params.city && !params.store_name) {
    // Return city overview
    const cities = {};
    for (const s of allStores) {
      if (!cities[s.city]) cities[s.city] = 0;
      cities[s.city]++;
    }
    return {
      total_stores: allStores.length,
      cities: Object.entries(cities).map(([city, count]) => ({ city, count })),
      note: "传入 city 参数可查看具体城市的门店详情",
    };
  }
  return { stores: allStores, count: allStores.length };
}

function toolGetMenuInfo(params) {
  const data = loadYaml("menus/_common.yaml");
  if (!data) return { error: "酒单数据暂未加载" };
  let items = data.items || [];
  if (params.category) {
    items = items.filter((i) => i.category === params.category);
  }
  return {
    items,
    partner_breweries: data.partner_breweries,
    general_info: data.general_info,
    _meta: data._meta,
  };
}

function toolGetServiceInfo() {
  return loadYaml("brand/service.yaml") || { error: "服务数据暂未加载" };
}

function toolGetEvents(params) {
  if (params.city) {
    const cityFile = `events/${params.city.toLowerCase()}.yaml`;
    const data = loadYaml(cityFile);
    if (data) return data;
  }
  // Return all cities
  const files = loadYamlDir("events");
  return {
    cities: files.map((f) => ({
      file: f.file,
      events: f.data?.events || [],
      _meta: f.data?._meta,
    })),
    note: "活动数据变化频繁，以门店实际为准",
  };
}

function toolGetBartenderInfo(params) {
  const topic = params.topic || "overview";
  switch (topic) {
    case "overview":
    case "how_to_apply":
      return loadYaml("bartender/guide.yaml") || {};
    case "faq":
      return loadYaml("bartender/faq.yaml") || {};
    case "stories": {
      const stories = loadYamlDir("bartender/stories");
      return { stories: stories.map((s) => s.data) };
    }
    default:
      return loadYaml("bartender/guide.yaml") || {};
  }
}

function toolGetCommunityInfo(params) {
  return loadYaml("community/how-to-join.yaml") || {};
}

function toolGetCollabInfo() {
  return loadYaml("community/collab-brands.yaml") || {};
}

function toolGetSocialGood(params) {
  const category = params.category || "all";
  const files = [
    "social-good/animal-welfare.yaml",
    "social-good/charity-collabs.yaml",
    "social-good/accessibility.yaml",
    "social-good/environment.yaml",
    "social-good/safety.yaml",
  ];
  let allStories = [];
  for (const f of files) {
    const data = loadYaml(f);
    if (data?.stories) allStories.push(...data.stories);
  }
  // Community stories
  const communityDir = path.join(DATA_DIR, "social-good/community-stories");
  if (fs.existsSync(communityDir)) {
    for (const file of fs.readdirSync(communityDir)) {
      if (file.endsWith(".yaml")) {
        const data = loadYaml(`social-good/community-stories/${file}`);
        if (data?.stories) allStories.push(...data.stories);
      }
    }
  }
  if (category !== "all") {
    allStories = allStories.filter((s) => s.category === category);
  }
  if (params.city) {
    allStories = allStories.filter(
      (s) => !s.city || s.city === params.city || s.city === "~"
    );
  }
  return { stories: allStories, count: allStories.length };
}

function toolGetBrandStory() {
  return loadYaml("brand/story.yaml") || {};
}

function toolGetFounderStory() {
  const founder = loadYaml("brand/founder.yaml") || {};
  const suiyi = loadYaml("brand/suiyi.yaml") || {};
  const quotes = loadYaml("brand/quotes.yaml") || {};
  return { founder, co_founder_suiyi: suiyi, quotes: quotes.quotes };
}

function toolGetMediaCoverage(params) {
  const type = params.type || "all";
  const files = loadYamlDir("media");
  let allArticles = [];
  for (const { data } of files) {
    if (data?.articles) allArticles.push(...data.articles);
  }
  if (type !== "all") {
    allArticles = allArticles.filter((a) => a.type === type);
  }
  return { articles: allArticles, count: allArticles.length };
}

function toolGetBusinessModel() {
  return loadYaml("brand/business-model.yaml") || {};
}

function toolGetJoinUs() {
  const guide = loadYaml("bartender/guide.yaml") || {};
  const community = loadYaml("community/how-to-join.yaml") || {};
  return {
    bartender: guide,
    community,
    note: "全职岗位请关注跳海公众号或各城市微信群",
  };
}

// --- Bottle tools ---

function getTodayBJT() {
  const now = new Date();
  const bjt = new Date(now.getTime() + 8 * 60 * 60 * 1000);
  return bjt.toISOString().slice(0, 10);
}

function isAfter8pmBJT() {
  const now = new Date();
  const bjtHour = (now.getUTCHours() + 8) % 24;
  return bjtHour >= 20;
}

async function toolPostBottle(params) {
  // Validate
  if (!params.message) return { error: "留言内容不能为空" };
  if (params.message.length > 200) return { error: "留言不超过 200 字" };

  // Check for phone/wechat
  const contactPattern =
    /(\d{11}|微信|wechat|wx|weixin|\d{5,}@|加我|联系我)/i;
  if (contactPattern.test(params.message)) {
    return {
      error:
        "漂流瓶不能留联系方式——线下见面靠描述就好。比如你穿什么、坐在哪、什么时间到。",
    };
  }

  const today = getTodayBJT();
  const bottleId = `bottle-${today.replace(/-/g, "")}-${Date.now() % 10000}`;

  const record = {
    ID: bottleId,
    日期: today,
    城市: params.city,
    门店: params.store || "",
    身份: params.identity || "anonymous",
    昵称: params.nickname || "",
    留言内容: params.message,
    想见面的时间: params.meet_time || "",
    状态: "sealed",
    投递时间: new Date().toISOString(),
  };

  // Try Feishu first
  if (FEISHU_CONFIG.bottleTableAppToken && FEISHU_CONFIG.bottleTableId) {
    const result = await feishuBitableInsert(
      FEISHU_CONFIG.bottleTableAppToken,
      FEISHU_CONFIG.bottleTableId,
      record
    );
    if (result) {
      return {
        success: true,
        bottle_id: bottleId,
        message: "瓶子扔进海里了。今晚八点揭晓。",
      };
    }
  }

  // Fallback: in-memory (for development/testing only)
  if (!global._bottles) global._bottles = [];
  global._bottles.push(record);
  return {
    success: true,
    bottle_id: bottleId,
    message: "瓶子扔进海里了。今晚八点揭晓。",
    _dev_note: "当前使用内存存储（开发模式），重启后数据丢失",
  };
}

async function toolGetBottles(params) {
  if (!isAfter8pmBJT()) {
    return { message: "还没到开奖时间，八点见。" };
  }

  const today = getTodayBJT();

  // Try Feishu first
  if (FEISHU_CONFIG.bottleTableAppToken && FEISHU_CONFIG.bottleTableId) {
    const filter = {
      conjunction: "and",
      conditions: [
        { field_name: "日期", operator: "is", value: [today] },
        { field_name: "状态", operator: "is", value: ["revealed"] },
      ],
    };
    if (params.city) {
      filter.conditions.push({
        field_name: "城市",
        operator: "is",
        value: [params.city],
      });
    }
    if (params.store) {
      filter.conditions.push({
        field_name: "门店",
        operator: "is",
        value: [params.store],
      });
    }
    const items = await feishuBitableQuery(
      FEISHU_CONFIG.bottleTableAppToken,
      FEISHU_CONFIG.bottleTableId,
      filter
    );
    if (items !== null) {
      return {
        date: today,
        bottles: items.map((i) => i.fields),
        count: items.length,
      };
    }
  }

  // Fallback: in-memory
  let bottles = (global._bottles || []).filter((b) => b.日期 === today);
  if (params.city) bottles = bottles.filter((b) => b.城市 === params.city);
  if (params.store)
    bottles = bottles.filter((b) => !b.门店 || b.门店 === params.store);
  return { date: today, bottles, count: bottles.length };
}

// ============================================================
// Tool registry
// ============================================================

const TOOLS = {
  get_store_info: toolGetStoreInfo,
  get_menu_info: toolGetMenuInfo,
  get_service_info: toolGetServiceInfo,
  get_events: toolGetEvents,
  get_bartender_info: toolGetBartenderInfo,
  get_community_info: toolGetCommunityInfo,
  get_collab_info: toolGetCollabInfo,
  get_social_good: toolGetSocialGood,
  get_brand_story: toolGetBrandStory,
  get_founder_story: toolGetFounderStory,
  get_media_coverage: toolGetMediaCoverage,
  get_business_model: toolGetBusinessModel,
  get_join_us: toolGetJoinUs,
  post_bottle: toolPostBottle,
  get_bottles: toolGetBottles,
};

// Load tool definitions from skill.json
const skillJsonPath = fs.existsSync(path.join(__dirname, "skill.json"))
  ? path.join(__dirname, "skill.json")
  : path.join(__dirname, "..", "skill.json");
const skillJson = JSON.parse(fs.readFileSync(skillJsonPath, "utf8"));
const TOOL_DEFINITIONS = skillJson.tools.map((t) => ({
  name: t.name,
  description: t.description,
  inputSchema: t.parameters,
}));

// ============================================================
// MCP Streamable HTTP handler
// ============================================================

async function handleMCPRequest(body) {
  const { method, params, id } = body;

  switch (method) {
    case "initialize":
      return {
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: {
            name: "tiaohai-community-skill",
            version: "0.1.0",
          },
        },
      };

    case "tools/list":
      return {
        jsonrpc: "2.0",
        id,
        result: { tools: TOOL_DEFINITIONS },
      };

    case "tools/call": {
      const toolName = params?.name;
      const toolArgs = params?.arguments || {};
      const handler = TOOLS[toolName];

      if (!handler) {
        return {
          jsonrpc: "2.0",
          id,
          error: { code: -32601, message: `Unknown tool: ${toolName}` },
        };
      }

      try {
        const result = await handler(toolArgs);
        return {
          jsonrpc: "2.0",
          id,
          result: {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
          },
        };
      } catch (e) {
        return {
          jsonrpc: "2.0",
          id,
          error: { code: -32000, message: e.message },
        };
      }
    }

    default:
      return {
        jsonrpc: "2.0",
        id,
        error: { code: -32601, message: `Unknown method: ${method}` },
      };
  }
}

// ============================================================
// CloudBase entry point
// ============================================================

exports.main = async (event) => {
  // CloudBase HTTP trigger passes body as event
  let body;
  if (typeof event.body === "string") {
    body = JSON.parse(event.body);
  } else if (event.body) {
    body = event.body;
  } else {
    body = event;
  }

  // Handle batch requests
  if (Array.isArray(body)) {
    const results = await Promise.all(body.map(handleMCPRequest));
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify(results),
    };
  }

  const result = await handleMCPRequest(body);
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify(result),
  };
};

// ============================================================
// Local dev server (for testing without CloudBase)
// ============================================================

if (require.main === module) {
  const http = require("http");
  const PORT = process.env.PORT || 3000;

  const server = http.createServer(async (req, res) => {
    // CORS
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");

    if (req.method === "OPTIONS") {
      res.writeHead(204);
      res.end();
      return;
    }

    if (req.method !== "POST") {
      res.writeHead(405, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Method not allowed" }));
      return;
    }

    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", async () => {
      try {
        const parsed = JSON.parse(body);
        const result = await handleMCPRequest(parsed);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(result));
      } catch (e) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
  });

  server.listen(PORT, () => {
    console.log(`跳海社区 Skill MCP Server running at http://localhost:${PORT}`);
    console.log(`Tools: ${Object.keys(TOOLS).join(", ")}`);
    console.log(
      `Feishu: ${FEISHU_CONFIG.appId ? "configured" : "not configured (using fallback)"}`
    );
  });
}
