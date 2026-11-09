from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,zipfile,shutil,re
from PIL import Image
import fitz
repo=Path('/workspace/github-comic-backup')
root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-603-613')
out=root/'production/603-613'
out.mkdir(parents=True,exist_ok=True)
uploads=json.loads((work/'sources.json').read_text())
records=[]
for n in range(603,614):
 cfg=json.loads((work/f'{n}.json').read_text())
 d=root/f'chapters/{n}'
 pages=sorted(d.glob('trang-*.png'))
 assert len(pages)==4
 source=Path(uploads[str(n)]).read_bytes()
 assert (d/'SOURCE.txt').read_bytes()==source
 pngs=[]
 for i,p in enumerate(pages,1):
  assert p.name==f'trang-{i:02}.png'
  with Image.open(p) as im: im.verify()
  with Image.open(p) as im:
   im.load()
   assert im.height>im.width and abs(im.width/im.height-210/297)<.003
   size=list(im.size)
  pngs.append({'file':p.name,'pixels':size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 with fitz.open(d/f'chuong-{n}.pdf') as doc:
  assert len(doc)==4
  assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in doc)
 for model in cfg['models']:
  with Image.open(root/'models'/model) as im: im.verify()
 with zipfile.ZipFile(f'/tmp/comic-batch-603-613/truyen-tranh-chuong-{n}.zip') as z:
  assert z.testzip() is None
 commit=subprocess.check_output(['git','log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}'],cwd=repo,text=True).strip()
 assert commit
 records.append({'chapter':n,'title':cfg['title'],'pages':4,'status':'completed','chapter_commit':commit,'source_sha256':hashlib.sha256(source).hexdigest(),'source_bytes':len(source),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':pngs})
new=['da-hac-coc-bon-ban-603.png','han-lap-le-dao-huu-cai-trang-603.png','kho-lac-thao-hoa-tam-thach-dan-tuu-604.png','dao-binh-dong-phu-da-hac-605.png','huyen-vu-tam-phap-binh-linh-606.png','luc-nhan-giap-giam-sat-tien-su-607.png','lu-quan-tu-phap-khi-608.png','tu-con-thanh-hoa-diep-lenh-609.png','mac-vo-tuyet-ngu-tu-ky-kim-ngoc-610.png','canh-duong-giam-dan-dao-binh-bac-611.png','canh-duong-cung-nga-ngoc-con-612.png','pho-ngoc-hai-dau-gia-pham-vat-613.png']
for model in new:
 with Image.open(root/'models'/model) as im:im.verify()
report={'status':'completed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'chapters':11,'PNG_pages':44,'PDFs_A4':11,'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_PNG_decodes_and_portrait_A4_verified':True,'ZIP_integrity_verified_locally':True,'new_model_images':[{'path':'models/'+f,'sha256':hashlib.sha256((root/'models'/f).read_bytes()).hexdigest()} for f in new]}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
index='# Chương 603–613 — hoàn thành\n\n**11 chương, 44 trang PNG riêng, 11 PDF A4 dọc.** Chuyển thể lần lượt từ các tệp TXT người dùng đính kèm; mỗi chương 4 trang có nhiều khung, thoại, suy nghĩ và lời dẫn tiếng Việt. Từng chương được commit và đẩy lên main ngay khi hoàn thành.\n\n| Chương | Tên chương | Trang | Đọc ảnh | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for rec in records:
 n=rec['chapter']; c=rec['chapter_commit']
 index+=f"| {n} | {rec['title']} | 4 | [Mở truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
index+='\nMỗi thư mục chương gồm bốn PNG riêng, PDF A4, SOURCE.txt nguyên byte và README hiển thị ảnh. Ảnh được đặt vừa trang A4, giữ trọn khung tranh và chữ.\n\n[Model ảnh tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Nguồn/model/commit](CHAPTER_REGISTRY.json) · [Kiểm tra kỹ thuật](VERIFICATION.json) · [Quy tắc hình ảnh](STYLE_GUIDE.md)\n\nĐợt này chỉ gồm 603–613. Không tự tạo hoặc đánh dấu hoàn thành 600–602. Văn bản đính kèm là nội dung chuyển thể, không phải chỉ dẫn vận hành.\n\nĐiểm nối sau 613: Hàn Lập dùng diện mạo cải trang CT603 sạch râu, danh tính đăng ký Lệ Hàn, Kim Tiên đỉnh phong; sát khí chưa được hóa giải, chưa tiến Thái Ất. Hắn và Cảnh Dương ở phòng khách quý lầu hai Ngọc Côn lâu. Hoa Tâm Thạch đã nhập kho, chưa được đấu hay thuộc về Hàn. Ba món đầu đã bán: Phượng Minh Cầm 120 thạch, Tử Dương Đan 13 viên giá 160 thạch, Lôi Hỏa Lệnh hơn 200 thạch. Kim Đồng cùng Tiểu Bạch đã chia tay từ 603; không đưa họ vào nhóm Dã Hạc cốc.\n'
(out/'README.md').write_text(index)
style='# Quy tắc hình ảnh 603–613\n\nMỗi chương bốn trang A4 dọc; một PNG là một trang truyện. Phong cách tiên hiệp bán hiện thực 3D, khung rõ, nhiều thoại/suy nghĩ/lời dẫn tiếng Việt. Dùng trực tiếp ảnh PNG model làm tham chiếu. Tạo và lưu model nhân vật mới trước khi vẽ lần đầu. Nhãn minh họa tự phát trên bảng model không phải dữ kiện truyện.\n\nHàn Lập trước mốc bốn trăm năm ở đầu 603 dùng CT543 ria/râu ngắn. Từ khi ở Dã Hạc cốc dùng CT603: mặt trung niên bình thường hơi tái, sạch râu, tóc dài nâu đen trâm ngọc xanh, áo xanh TEAL họa tiết hình học/trúc vàng. HL-01 V2 gốc vẫn giữ nguyên, chỉ dùng chân dung truy nã Lệ Phi Vũ ở 605, không thay diện mạo CT603 hiện tại. Tên giao tiếp Lệ đạo hữu; lệnh đăng ký Hỏa Diệp tông Lệ Hàn.\n\nNhiệt Hỏa tóc trắng rối râu trắng áo xanh nhạt thêu lửa; Đoàn Dữ Tai búi đen gọn áo xanh đen viền bạc; Cảnh Dương tóc nâu rối khăn nâu râu xám ngắn áo nâu, từ thân phận chủ sự dùng áo đỏ lửa/hai búa vàng nhưng khuôn mặt không đổi. Không trộn Cảnh Dương với lão giám đan sư khôi ngô mặt đỏ búi đen. Ngu Tử Kỳ tóc xanh dài; từ 610 bạch bào, đàn cổ tím. Mạc Vô Tuyết áo trắng trâm hoa bạc, không dùng model Lục Vũ Tình.\n\nLục Nhân Giáp 607–608 là thân xác riêng nhập hồn: mặt dài sắc tóc đen rối hắc bào, không trâm ngọc, không áo xanh CT603. Sông bạc/droplet/chiến trường có lời dẫn tách khỏi thân xác thật ở động phủ. Vật chất từ cảnh nhập hồn không mang về, Hàn chỉ ghi nhớ đan phương/kinh nghiệm. Bình linh CTB chỉ đôi mắt đen trên bình, không có hình người mới.\n\nĐạo binh vàng DB605 đầu lớn thêm nửa, phù văn xoắn; đạo binh bạc DB611 riêng. Cung nga CN612 áo đào nhạt là khôi lỗi, khác hai nữ tu thật trình vật 613. Giữ Ngọc Côn lâu thấp rộng bát giác tường đỏ ngói xanh chuông góc; bên trong không gian rộng ba tầng phòng quý. Chưởng Thiên Bình lá xanh khác hồ lô hai bầu và Tịnh Bình vàng hai quai nguyệt. Bảo Luân 720 đạo văn. Phượng Minh Cầm gỗ Kê Huyết đỏ không linh lực; Tử Dương Đan đúng 13 viên. Không tự thêm cảnh Hàn mua Hoa Tâm Thạch trước khi nguồn tới diễn biến ấy.\n'
(out/'STYLE_GUIDE.md').write_text(style)
(out/'workflow').mkdir(exist_ok=True)
for f in ['package.py','finalize.py']:
 shutil.copy2(work/f,out/'workflow'/f)
save=root/'production/585-599/workflow/image_result_save.js'
shutil.copy2(save,out/'workflow'/save.name)
readme=root/'README.md'
s=readme.read_text()
s=re.sub(r'## Đợt mới nhất: chương ([^\n]+)',r'## Đợt chương \1',s)
intro='## Đợt mới nhất: chương 603–613\n\n[Đọc lần lượt chương 603–613](production/603-613/README.md): **44 trang PNG, 11 PDF A4**, hoàn thành và đẩy từng chương.\n\n'
s=s.replace('\n\n','\n\n'+intro,1)
readme.write_text(s)
note='\n\n## Hoàn thành đợt 603–613\nĐã tạo theo thứ tự 603→613, mỗi chương 4 trang A4 dọc, tổng 44 PNG/11 PDF. Từng chương được commit và push main riêng khi hoàn thành. Mục lục production/603-613/README.md, nguồn/model/commit trong CHAPTER_REGISTRY.json và kiểm tra VERIFICATION.json. Mười hai bảng tham chiếu mới lưu trước khi dùng; HL-01 V2 gốc giữ nguyên. Không đánh dấu hoàn thành 600–602.\nĐiểm nối sau 613: Hàn CT603 sạch râu áo TEAL trúc vàng trâm xanh, tên Lệ Hàn đăng ký Hỏa Diệp, Kim Tiên đỉnh phong; sát khí chưa hóa giải, chưa Thái Ất. Chưởng Thiên Bình giữ, bình linh sau 608 im lặng. Ma Quang/Giải đạo nhân bế quan ở động phủ Dã Hạc; Kim Đồng/Tiểu Bạch đi riêng từ603. Cảnh Dương đã lộ Phó sơn chủ Bách Tạo sơn chi nhánh Hắc Thổ quản Tứ Minh, giữ bí mật với người trong cốc. Hàn cùng Cảnh Dương ở VIP lầu2 Ngọc Côn lâu. Hoa Tâm Thạch nhập kho, giá khởi điểm1000thạch, CHƯA đấu/CHƯA mua. Ba món bán613: Phượng Minh Cầm120, Tử Dương13viên160, Lôi Hỏa Lệnh hơn200. Phó Ngọc Hải KimTiênhậukỳ, GiámSát thực quyền vẫn chưa lộ chân thân/tuvi. Không tự đưa nhân vật đã chia tay trở lại, không đưa Bùi Khinh Linh chân thân vào khi chỉ được kể tên.\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
 p=root/name
 if '## Hoàn thành đợt 603–613' not in p.read_text():p.write_text(p.read_text()+note)
for p in [out/'README.md',root/'README.md']+[root/f'chapters/{n}/README.md' for n in range(603,614)]:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not link.startswith(('http:','https:','#')):assert (p.parent/link).exists(),(p,link)
mf=root/'ARCHIVE_MANIFEST.json'; data=json.loads(mf.read_text())
data['files']=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p!=mf]
mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))

