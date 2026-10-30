// k6/crud_load_test.js
// Kịch bản k6 mở rộng: Kiểm thử hiệu năng luồng nghiệp vụ CRUD cho CloudTask
//
// LƯU Ý BẢO MẬT VÀ TOÀN VẸN DỮ LIỆU:
// Kịch bản này thực hiện các thao tác Create - Read - Update - Delete (CRUD).
// CHỈ CHẠY trên môi trường Staging / Testing Database độc lập.
// TUYỆT ĐỐI KHÔNG CHẠY TRỰC TIẾP LÊN PRODUCTION DATABASE ĐANG DÙNG CỦA ĐỒ ÁN.
//
// Cách chạy:
//   k6 run -e TARGET_URL=http://localhost:5000 -e TEST_USER=admin@cloudtask.com -e TEST_PASSWORD=Password123! k6/crud_load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

export const crudDuration = new Trend('crud_req_duration');
export const crudErrorRate = new Rate('crud_error_rate');
export const tasksCreated = new Counter('tasks_created_count');
export const tasksDeleted = new Counter('tasks_deleted_count');

export const options = {
  stages: [
    { duration: '15s', target: 5 },   // Ramp-up nhẹ nhàng với 5 người dùng ảo
    { duration: '30s', target: 10 },  // Duy trì tải 10 VUs cho giao dịch ghi CSDL
    { duration: '15s', target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2500'], // Thao tác ghi DB p95 dưới 2.5s
    crud_error_rate: ['rate<0.05'],    // Tỷ lệ lỗi dưới 5%
  },
};

const BASE_URL = __ENV.TARGET_URL || 'http://localhost:5000';
const USER_EMAIL = __ENV.TEST_USER || 'admin@cloudtask.com';
const USER_PASS = __ENV.TEST_PASSWORD || 'Password123!';

// Trích xuất CSRF Token từ thẻ input hidden do Flask-WTF render
function extractCsrfToken(body) {
  if (!body) return '';
  const match = body.match(/name=["']csrf_token["'][^>]*value=["']([^"']+)["']/) ||
                body.match(/value=["']([^"']+)["'][^>]*name=["']csrf_token["']/);
  return match ? match[1] : '';
}

// Trích xuất task ID đầu tiên tìm thấy trong HTML danh sách tasks
function extractFirstTaskId(body) {
  if (!body) return null;
  const match = body.match(/\/tasks\/(\d+)\/edit/);
  return match ? match[1] : null;
}

export default function () {
  const jar = http.cookieJar();

  // 1. GET /login để lấy CSRF token
  const getLoginRes = http.get(`${BASE_URL}/login`);
  check(getLoginRes, { 'GET /login 200': (r) => r.status === 200 });
  const loginCsrf = extractCsrfToken(getLoginRes.body);

  // 2. POST /login xác thực lấy phiên làm việc (Session Cookie)
  const loginPayload = {
    email: USER_EMAIL,
    password: USER_PASS,
  };
  if (loginCsrf) loginPayload.csrf_token = loginCsrf;

  const loginRes = http.post(`${BASE_URL}/login`, loginPayload, {
    redirects: 1,
  });

  const loggedIn = check(loginRes, {
    'login successful': (r) => r.status === 200 || r.status === 302,
  });

  if (!loggedIn) {
    crudErrorRate.add(1);
    sleep(1);
    return;
  }

  // 3. READ: Tải danh sách công việc
  const listRes = http.get(`${BASE_URL}/tasks`);
  check(listRes, { 'GET /tasks 200': (r) => r.status === 200 });
  crudDuration.add(listRes.timings.duration);

  // 4. GET /tasks/new để lấy CSRF token tạo task mới
  const getNewRes = http.get(`${BASE_URL}/tasks/new`);
  const createCsrf = extractCsrfToken(getNewRes.body);

  // 5. CREATE: Thêm mới công việc vào CSDL
  const uniqueTitle = `k6-task-${__VU}-${Date.now()}`;
  const createPayload = {
    title: uniqueTitle,
    description: 'Automated performance transaction created by k6 CRUD suite.',
    priority: 'medium',
    status: 'pending',
  };
  if (createCsrf) createPayload.csrf_token = createCsrf;

  const createRes = http.post(`${BASE_URL}/tasks/new`, createPayload, {
    redirects: 1,
  });

  const createdOk = check(createRes, {
    'CREATE task completed': (r) => r.status === 200 || r.status === 302,
  });

  if (createdOk) {
    tasksCreated.add(1);
    crudErrorRate.add(0);
  } else {
    crudErrorRate.add(1);
  }
  crudDuration.add(createRes.timings.duration);

  // 6. READ + DELETE: Dọn dẹp task vừa tạo (để bảo vệ tải và dung lượng DB)
  const afterListRes = http.get(`${BASE_URL}/tasks`);
  const deleteCsrf = extractCsrfToken(afterListRes.body);
  const taskId = extractFirstTaskId(afterListRes.body);

  if (taskId && deleteCsrf) {
    const deletePayload = { csrf_token: deleteCsrf };
    const deleteRes = http.post(`${BASE_URL}/tasks/${taskId}/delete`, deletePayload, {
      redirects: 1,
    });
    if (check(deleteRes, { 'DELETE task completed': (r) => r.status === 200 || r.status === 302 })) {
      tasksDeleted.add(1);
    }
  }

  sleep(1);
}
